#!/usr/bin/env python3
"""
yummyballs script (pypy3)
version 1.0

"""

import curses, random, time, os, sys

HIGHSCORE_FILE = os.path.expanduser("~/.yummyballs_highscore")

def load_highscore():
    try:
        with open(HIGHSCORE_FILE, "r") as f:
            return int(f.read().strip())
    except:
        return 0

def save_highscore(score):
    try:
        with open(HIGHSCORE_FILE, "w") as f:
            f.write(str(score))
    except:
        pass

def safe_addch(win, y, x, ch, attr=0):
    try:
        win.addch(y, x, ch, attr)
    except curses.error:
        pass

def safe_addstr(win, y, x, s, attr=0):
    try:
        if attr:
            win.addstr(y, x, s, attr)
        else:
            win.addstr(y, x, s)
    except curses.error:
        pass

def make_row(width, density, gold_row_chance=0.0):
    row = [" " for _ in range(width)]
    for x in range(width):
        if random.random() < density:
            r = random.random()
            if r < 0.7:
                row[x] = "#"
            elif r < 0.9:
                row[x] = "X"
            else:
                row[x] = "+"
    # occasionally plant a gold O in the row (represents rare jackpot)
    if random.random() < gold_row_chance:
        pos = random.randrange(0, width)
        row[pos] = "G"
    return row

def clamp(v, lo, hi):
    return max(lo, min(v, hi))

def safe_tile_read(ground, y, x):
    """Return a safe tile character for (y,x). Treat anything wrong as ' '."""
    try:
        ch = ground[y][x]
        if not isinstance(ch, str) or len(ch) == 0:
            return " "
        return ch
    except Exception:
        return " "

def main(stdscr):
    # minimal setup
    try: curses.curs_set(0)
    except: pass
    curses.noecho()
    curses.cbreak()
    stdscr.nodelay(True)

    # NEW: safe init_pair wrapper
    def safe_init_pair(pair, fg, bg):
        try:
            curses.init_pair(pair, fg, bg)
        except ValueError:
            curses.init_pair(pair, fg, curses.COLOR_BLACK)

    use_colors = False
    if curses.has_colors():
        curses.start_color()
        curses.use_default_colors()
        safe_init_pair(1, curses.COLOR_BLUE, -1)   # Ball (normal)
        safe_init_pair(2, curses.COLOR_WHITE, -1)  # Normal walls
        safe_init_pair(3, curses.COLOR_RED, -1)    # Death walls / death ball display
        safe_init_pair(4, curses.COLOR_GREEN, -1)  # Bonus +
        safe_init_pair(5, curses.COLOR_RED, -1)    # Ball (immune/red)
        safe_init_pair(6, curses.COLOR_YELLOW, -1) # Gold O
        use_colors = True

    maxy, maxx = stdscr.getmaxyx()
    width = min(20, maxx - 12)
    height = min(20, maxy - 2)

    if width < 10 or height < 6:
        stdscr.erase()
        safe_addstr(stdscr, 0, 0, "terminal too small for yummyballs")
        stdscr.refresh()
        stdscr.getch()
        return

    ball_x, ball_y = width // 2, height // 2

    # difficulty vars
    base_density = 0.01
    density = base_density
    max_density = 0.9
    density_step = 0.01

    score = 0
    tick = 0
    delay = 0.17
    min_delay = 0.05
    highscore = load_highscore()

    # immunity / noclip vars
    immunity_duration = 20.0  # seconds you can noclip
    immunity_check_interval = 20.0  # roll every 20s
    immunity_chance = 1/10.0
    last_immunity_check = time.perf_counter()
    immune_until = 0.0  # timestamp until which immunity is active

    # gold multiplier settings (hardcoded spawn frequency)
    gold_row_chance = 4.0 / 300.0
    gold_multiplier = 3
    gold_duration = 40.0
    gold_until = 0.0  # timestamp until which gold is active

    # init map
    ground = [make_row(width, density, gold_row_chance) for _ in range(height)]
    ground[ball_y][ball_x] = " "

    # countdown
    for i in range(3, 0, -1):
        stdscr.erase()
        safe_addstr(stdscr, height//2, (width//2)-1, str(i))
        stdscr.noutrefresh(); curses.doupdate()
        time.sleep(1)
    stdscr.erase()
    safe_addstr(stdscr, height//2, (width//2)-2, "GO!")
    stdscr.noutrefresh(); curses.doupdate()
    time.sleep(0.5)

    last_frame = time.perf_counter()

    while True:
        now = time.perf_counter()

        # --- INPUT & MOVEMENT ---
        key = stdscr.getch()
        if key == ord("a") and ball_x > 0: ball_x -= 1
        if key == ord("l") and ball_x < width-1: ball_x += 1
        if key == ord("e"): break

        ball_x = clamp(ball_x, 0, width - 1)
        ball_y = clamp(ball_y, 0, height - 1)

        # --- IMMUNITY ROLL ---
        if now - last_immunity_check >= immunity_check_interval:
            last_immunity_check = now
            if random.random() < immunity_chance:
                immune_until = now + immunity_duration
                try: curses.beep()
                except: pass
                if 0 <= ball_y < height and 0 <= ball_x < width:
                    if ground[ball_y][ball_x] in ("#", "X"):
                        ground[ball_y][ball_x] = " "

        immune = time.perf_counter() < immune_until
        gold_active = time.perf_counter() < gold_until
        score_multiplier = gold_multiplier if gold_active else 1

        if immune and 0 <= ball_y < height and 0 <= ball_x < width:
            if ground[ball_y][ball_x] in ("#", "X"):
                ground[ball_y][ball_x] = " "

        # --- COLLISION ---
        ch = safe_tile_read(ground, ball_y, ball_x)
        if ch in ("#", "X"):
            if not immune:
                stdscr.erase()
                for y in range(height):
                    for x in range(width):
                        t = ground[y][x]
                        if t == "#":
                            safe_addch(stdscr, y, x, t, curses.color_pair(2) if use_colors else 0)
                        elif t == "X":
                            safe_addch(stdscr, y, x, t, curses.color_pair(3) if use_colors else 0)
                        elif t == "+":
                            safe_addch(stdscr, y, x, t, curses.color_pair(4) if use_colors else 0)
                        elif t == "G":
                            safe_addch(stdscr, y, x, "O", curses.color_pair(6) if use_colors else 0)
                        else:
                            safe_addch(stdscr, y, x, " ")
                safe_addch(stdscr, ball_y, ball_x, "O", curses.color_pair(3) if use_colors else 0)
                stdscr.noutrefresh(); curses.doupdate()
                time.sleep(0.08)
                break
            else:
                ground[ball_y][ball_x] = " "
        elif ch == "+":
            score += 5 * score_multiplier
            ground[ball_y][ball_x] = " "
        elif ch == "G":
            gold_until = time.perf_counter() + gold_duration
            try: curses.flash()
            except: pass
            ground[ball_y][ball_x] = " "

        # --- SCROLL / MAP UPDATE ---
        tick += 1
        if tick % 2 == 0:
            ground.pop(0)
            ground.append(make_row(width, density, gold_row_chance))
            score += 1 * score_multiplier

            if score % 20 == 0:
                if delay > min_delay:
                    delay = max(min_delay, delay - 0.01)
                if density < max_density:
                    density = min(max_density, density + density_step)

            ball_x = clamp(ball_x, 0, width - 1)
            ball_y = clamp(ball_y, 0, height - 1)
            if immune and 0 <= ball_y < height and 0 <= ball_x < width:
                if ground[ball_y][ball_x] in ("#", "X"):
                    ground[ball_y][ball_x] = " "

        # --- DRAW ---
        stdscr.erase()
        for y in range(height):
            for x in range(width):
                t = ground[y][x]
                if t == "#":
                    safe_addch(stdscr, y, x, t, curses.color_pair(2) if use_colors else 0)
                elif t == "X":
                    safe_addch(stdscr, y, x, t, curses.color_pair(3) if use_colors else 0)
                elif t == "+":
                    safe_addch(stdscr, y, x, t, curses.color_pair(4) if use_colors else 0)
                elif t == "G":
                    safe_addch(stdscr, y, x, "O", curses.color_pair(6) if use_colors else 0)
                else:
                    safe_addch(stdscr, y, x, " ")

        ball_attr = curses.color_pair(5) if (use_colors and immune) else (curses.color_pair(1) if use_colors else 0)
        safe_addch(stdscr, ball_y, ball_x, "O", ball_attr)

        safe_addstr(stdscr, 0, width+2, f"score: {score}   ")
        safe_addstr(stdscr, 1, width+2, f"high: {highscore}   ")
        safe_addstr(stdscr, 3, width+2, f"dens: {density:.2f}")
        if immune:
            safe_addstr(stdscr, 5, width+2, f"IMMUNE! {max(0, immune_until - time.perf_counter()):.1f}s ")
        else:
            next_check_in = max(0.0, immunity_check_interval - (time.perf_counter() - last_immunity_check))
            safe_addstr(stdscr, 5, width+2, f"next roll: {next_check_in:.1f}s ")
        if gold_active:
            safe_addstr(stdscr, 7, width+2, f"GOLD x{gold_multiplier}! {max(0, gold_until - time.perf_counter()):.1f}s ")
        else:
            safe_addstr(stdscr, 7, width+2, "gold: none       ")

        stdscr.noutrefresh(); curses.doupdate()

        # --- FRAME TIMING ---
        to_sleep = delay - (time.perf_counter() - last_frame)
        if to_sleep > 0:
            time.sleep(to_sleep)
        last_frame = time.perf_counter()

    # game over
    stdscr.erase()
    safe_addstr(stdscr, height//2, (width//2)-5, "GAME OVER LMAO")
    if score > highscore:
        save_highscore(score)
        safe_addstr(stdscr, height//2+1, (width//2)-7, f"you got a new high score: {score}")
    else:
        safe_addstr(stdscr, height//2+1, (width//2)-5, f"score: {score}")
    stdscr.noutrefresh(); curses.doupdate()
    stdscr.nodelay(False); stdscr.getch()

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        sys.exit(0)
# yummyballs

a small terminal arcade game written in python using curses.

dodge falling obstacles, collect bonuses, and try to survive as the game speeds up. the longer you survive, the harder it gets!

# features

- increasing difficulty over time
- collectible bonus tiles ("+")
- rare gold bonus multiplier ("O")
- temporary events
- persistent high score
- other stuff

# gameplay

you control the ball ("O") and must avoid obstacles as the map scrolls upward.

controls

key| action.  
"a"| move left.  
"l"| move right.  
"e"| exit game.  

tiles

symbol| meaning.  
"O"| player.  
"#"| obstacle.  
"X"| deadly obstacle.  
"+"| bonus score.  
"G"| gold bonus (score multiplier)   

# installation

clone the repository:

```
git clone https://github.com/auth1ery/yummyballs.git
cd yummyballs
```

run the installer:

```
chmod +x install.sh
./install.sh
```

the installer will:

- detect your linux distribution
- install pypy3 if needed
- verify curses support
- install the launcher command

after installation, run the game with:

```
yummyballs
```

# requirements

- linux
- terminal that supports curses

supported package managers:

- dnf
- apt
- pacman
- zypper

---

have fun :)
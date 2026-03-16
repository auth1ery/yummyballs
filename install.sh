#!/usr/bin/env bash

set -e

# ----- colors -----

if command -v tput >/dev/null 2>&1 && [ "$(tput colors)" -ge 8 ]; then
    GREEN=$(tput setaf 2)
    RED=$(tput setaf 1)
    YELLOW=$(tput setaf 3)
    BLUE=$(tput setaf 4)
    RESET=$(tput sgr0)
else
    GREEN=""
    RED=""
    YELLOW=""
    BLUE=""
    RESET=""
fi

info() {
    echo "${BLUE}info:${RESET} $1"
}

success() {
    echo "${GREEN}success:${RESET} $1"
}

warn() {
    echo "${YELLOW}warning:${RESET} $1"
}

error() {
    echo "${RED}error:${RESET} $1"
    exit 1
}

# ----- start -----

info "starting yummyballs installer"

if [ ! -f "yummyballs.py" ]; then
    error "yummyballs.py not found in this directory"
fi

info "detecting package manager"

PM=""

if command -v dnf >/dev/null 2>&1; then
    PM="dnf"
elif command -v apt >/dev/null 2>&1; then
    PM="apt"
elif command -v pacman >/dev/null 2>&1; then
    PM="pacman"
elif command -v zypper >/dev/null 2>&1; then
    PM="zypper"
fi

[ -z "$PM" ] && error "no supported package manager detected (dnf apt pacman zypper)"

info "package manager detected: $PM"

# ----- install pypy3 -----

if command -v pypy3 >/dev/null 2>&1; then
    success "pypy3 already installed"
else
    info "installing pypy3"

    case $PM in
        dnf)
            sudo dnf install -y pypy3
            ;;
        apt)
            sudo apt update
            sudo apt install -y pypy3
            ;;
        pacman)
            sudo pacman -Sy --noconfirm pypy
            ;;
        zypper)
            sudo zypper install -y pypy3
            ;;
    esac

    success "pypy3 installed"
fi

# ----- check curses -----

info "checking curses support in pypy3"

if ! pypy3 - <<EOF >/dev/null 2>&1
import curses
EOF
then
    warn "curses module failed to load in pypy3"
    warn "installing ncurses packages"

    case $PM in
        dnf)
            sudo dnf install -y ncurses ncurses-devel
            ;;
        apt)
            sudo apt install -y libncurses5 libncurses5-dev
            ;;
        pacman)
            sudo pacman -Sy --noconfirm ncurses
            ;;
        zypper)
            sudo zypper install -y ncurses-devel
            ;;
    esac
else
    success "curses module available"
fi

# ----- install script -----

INSTALL_DIR="/usr/local/share/yummyballs"
BIN_PATH="/usr/local/bin/yummyballs"

info "creating install directory: $INSTALL_DIR"
sudo mkdir -p "$INSTALL_DIR"

info "copying yummyballs.py"
sudo cp yummyballs.py "$INSTALL_DIR/yummyballs.py"

info "creating launcher command"

sudo tee "$BIN_PATH" >/dev/null <<EOF
#!/usr/bin/env bash
pypy3 $INSTALL_DIR/yummyballs.py "\$@"
EOF

sudo chmod +x "$BIN_PATH"

success "installation complete"
info "run the game by typing: yummyballs"
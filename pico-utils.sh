#!/bin/bash
# Utilities for MicroPython Pico management

PORT="${PICO_PORT:-/dev/ttyACM0}"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

show_help() {
    echo "Pico Utilities - Quick commands for MicroPython development"
    echo ""
    echo "Usage: ./pico-utils.sh COMMAND"
    echo ""
    echo "Commands:"
    echo "  ls          - List files on Pico"
    echo "  tree        - Show file tree on Pico"
    echo "  clean       - Remove all .py files from Pico"
    echo "  reset       - Soft reset the Pico"
    echo "  repl        - Connect to REPL (screen)"
    echo "  backup      - Backup all files from Pico"
    echo "  get FILE    - Download FILE from Pico"
    echo "  rm FILE     - Remove FILE from Pico"
    echo "  run FILE    - Run FILE on Pico"
    echo ""
    echo "Environment:"
    echo "  PICO_PORT   - Serial port (default: /dev/ttyACM0)"
    echo "              export PICO_PORT=/dev/ttyUSB0"
}

cmd_ls() {
    echo -e "${BLUE}Files on Pico:${NC}"
    ampy --port "$PORT" ls
}

cmd_tree() {
    echo -e "${BLUE}File tree on Pico:${NC}"
    echo "/"
    ampy --port "$PORT" ls / 2>/dev/null | while read -r item; do
        echo "├── $item"
        if [[ "$item" == *"/"* ]] || [[ -z "${item##*[/]}" ]]; then
            ampy --port "$PORT" ls "$item" 2>/dev/null | while read -r subitem; do
                echo "│   ├── $subitem"
            done
        fi
    done
}

cmd_clean() {
    echo -e "${YELLOW}WARNING: This will remove main.py and all modules!${NC}"
    read -p "Are you sure? (yes/no): " confirm
    if [ "$confirm" = "yes" ]; then
        echo "Removing files..."
        ampy --port "$PORT" rm main.py 2>/dev/null || true
        ampy --port "$PORT" rmdir core 2>/dev/null || true
        ampy --port "$PORT" rmdir apps 2>/dev/null || true
        echo -e "${GREEN}Done!${NC}"
    else
        echo "Cancelled"
    fi
}

cmd_reset() {
    echo -e "${BLUE}Resetting Pico...${NC}"
    echo -e "\x04" > "$PORT"
    echo -e "${GREEN}Reset signal sent${NC}"
}

cmd_repl() {
    echo -e "${BLUE}Connecting to REPL (Ctrl+A then K to exit)${NC}"
    screen "$PORT" 115200
}

cmd_backup() {
    BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    echo -e "${BLUE}Backing up to $BACKUP_DIR${NC}"
    
    ampy --port "$PORT" ls / | while read -r file; do
        if [[ "$file" == *.py ]] || [[ "$file" == *.json ]]; then
            echo "  → $file"
            ampy --port "$PORT" get "$file" "$BACKUP_DIR/$file" 2>/dev/null || true
        fi
    done
    
    echo -e "${GREEN}Backup complete!${NC}"
}

cmd_get() {
    if [ -z "$1" ]; then
        echo "Usage: $0 get FILENAME"
        exit 1
    fi
    echo -e "${BLUE}Downloading $1${NC}"
    ampy --port "$PORT" get "$1"
}

cmd_rm() {
    if [ -z "$1" ]; then
        echo "Usage: $0 rm FILENAME"
        exit 1
    fi
    echo -e "${YELLOW}Removing $1${NC}"
    ampy --port "$PORT" rm "$1"
    echo -e "${GREEN}Done!${NC}"
}

cmd_run() {
    if [ -z "$1" ]; then
        echo "Usage: $0 run FILENAME"
        exit 1
    fi
    echo -e "${BLUE}Running $1${NC}"
    ampy --port "$PORT" run "$1"
}

# Main
if [ $# -eq 0 ]; then
    show_help
    exit 0
fi

COMMAND=$1
shift

case "$COMMAND" in
    ls)
        cmd_ls
        ;;
    tree)
        cmd_tree
        ;;
    clean)
        cmd_clean
        ;;
    reset)
        cmd_reset
        ;;
    repl)
        cmd_repl
        ;;
    backup)
        cmd_backup
        ;;
    get)
        cmd_get "$@"
        ;;
    rm)
        cmd_rm "$@"
        ;;
    run)
        cmd_run "$@"
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "Unknown command: $COMMAND"
        echo ""
        show_help
        exit 1
        ;;
esac


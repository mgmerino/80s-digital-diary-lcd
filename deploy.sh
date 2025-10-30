#!/bin/bash
# Deploy script for MicroPython Pico
# Only uploads modified files to save time

set -e  # Exit on error

# Configuration
PORT="${PICO_PORT:-/dev/ttyACM1}"
CACHE_FILE=".deploy_cache"
FORCE_UPLOAD=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -f|--force)
            FORCE_UPLOAD=true
            shift
            ;;
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [-f|--force] [-p|--port PORT]"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}=== MicroPython Deployment Script ===${NC}"
echo -e "${BLUE}Port: ${PORT}${NC}"
echo ""

# Check if ampy is installed
if ! command -v ampy &> /dev/null; then
    echo -e "${RED}Error: ampy is not installed${NC}"
    echo "Install it with: pip install adafruit-ampy"
    exit 1
fi

# Check if device is connected
if [ ! -e "$PORT" ]; then
    echo -e "${RED}Error: Device not found at ${PORT}${NC}"
    echo "Available ports:"
    ls /dev/ttyACM* /dev/ttyUSB* 2>/dev/null || echo "  None found"
    exit 1
fi

# Create cache file if it doesn't exist
touch "$CACHE_FILE"

# Function to get file hash
get_hash() {
    md5sum "$1" 2>/dev/null | cut -d' ' -f1
}

# Function to check if file needs upload
needs_upload() {
    local file="$1"
    local current_hash=$(get_hash "$file")
    local cached_hash=$(grep "^$file:" "$CACHE_FILE" 2>/dev/null | cut -d':' -f2)
    
    if [ "$FORCE_UPLOAD" = true ]; then
        return 0  # Always upload
    fi
    
    if [ "$current_hash" != "$cached_hash" ]; then
        return 0  # Hash changed, needs upload
    else
        return 1  # Hash same, skip upload
    fi
}

# Function to update cache
update_cache() {
    local file="$1"
    local hash=$(get_hash "$file")
    # Remove old entry and add new one (use @ as delimiter to handle / in paths)
    sed -i "\@^$file:@d" "$CACHE_FILE" 2>/dev/null || true
    echo "$file:$hash" >> "$CACHE_FILE"
}

# Function to upload file
upload_file() {
    local local_path="$1"
    local remote_path="$2"
    
    if needs_upload "$local_path"; then
        echo -e "${YELLOW}→ Uploading: ${local_path}${NC}"
        if ampy --port "$PORT" put "$local_path" "$remote_path" 2>&1; then
            echo -e "${GREEN}✓ Uploaded: ${local_path}${NC}"
            update_cache "$local_path"
            return 0
        else
            echo -e "${RED}✗ Failed: ${local_path}${NC}"
            return 1
        fi
    else
        echo -e "${BLUE}⊙ Skipped (unchanged): ${local_path}${NC}"
        return 0
    fi
}

# Function to create directory if it doesn't exist
ensure_dir() {
    local dir="$1"
    echo -e "${YELLOW}→ Ensuring directory: ${dir}${NC}"
    ampy --port "$PORT" mkdir "$dir" 2>/dev/null || true
    echo -e "${GREEN}✓ Directory ready: ${dir}${NC}"
}

# Start deployment
echo -e "${RED}* * * Creating secrets * * *${NC}"
upload_file "secrets.py" "secrets.py"

echo -e "${BLUE}--- Phase 1: Creating directories ---${NC}"
ensure_dir "core"
ensure_dir "apps"
ensure_dir "hal"
ensure_dir "hal/real"
ensure_dir "assets"
echo ""

echo -e "${BLUE}--- Phase 2: Uploading HAL modules ---${NC}"
upload_file "hal/__init__.py" "hal/__init__.py"
upload_file "hal/color.py" "hal/color.py"
upload_file "hal/interfaces.py" "hal/interfaces.py"
upload_file "hal/platform.py" "hal/platform.py"
upload_file "hal/real/__init__.py" "hal/real/__init__.py"
upload_file "hal/real/backlight.py" "hal/real/backlight.py"
upload_file "hal/real/clock.py" "hal/real/clock.py"
upload_file "hal/real/display.py" "hal/real/display.py"
upload_file "hal/real/input.py" "hal/real/input.py"
upload_file "hal/real/storage.py" "hal/real/storage.py"
echo ""

echo -e "${BLUE}--- Phase 3: Uploading core modules ---${NC}"
upload_file "core/__init__.py" "core/__init__.py"
upload_file "core/context.py" "core/context.py"
upload_file "core/ui.py" "core/ui.py"
upload_file "core/input.py" "core/input.py"
upload_file "core/utils.py" "core/utils.py"
upload_file "core/wifi_manager.py" "core/wifi_manager.py"
upload_file "core/ntp_sync.py" "core/ntp_sync.py"
upload_file "core/timezone_manager.py" "core/timezone_manager.py"
echo ""

echo -e "${BLUE}--- Phase 4: Uploading app modules ---${NC}"
upload_file "apps/__init__.py" "apps/__init__.py"
upload_file "apps/base.py" "apps/base.py"
upload_file "apps/clock.py" "apps/clock.py"
upload_file "apps/calculator.py" "apps/calculator.py"
upload_file "apps/settings.py" "apps/settings.py"
upload_file "apps/calendar.py" "apps/calendar.py"
upload_file "apps/contacts.py" "apps/contacts.py"
upload_file "apps/memos.py" "apps/memos.py"
upload_file "apps/games.py" "apps/games.py"
upload_file "apps/moonphase.py" "apps/moonphase.py"
upload_file "apps/settime.py" "apps/settime.py"
upload_file "apps/theme_chooser.py" "apps/theme_chooser.py"
upload_file "apps/w_brightness.py" "apps/w_brightness.py"
upload_file "apps/todos.py" "apps/todos.py"

echo -e "${BLUE}--- Phase 5: Uploading assets ---${NC}"
upload_file "assets/quotes.txt" "assets/quotes.txt"
echo ""

echo -e "${BLUE}--- Phase 6: Uploading main file ---${NC}"
if [ -f "main.py" ]; then
    upload_file "main.py" "main.py"
else
    echo -e "${YELLOW}Warning: main.py not found, skipping${NC}"
fi
echo ""

echo -e "${GREEN}=== Deployment complete! ===${NC}"
echo ""
echo -e "${BLUE}To reset the cache and force re-upload all files:${NC}"
echo -e "  rm $CACHE_FILE && ./deploy.sh"
echo ""
echo -e "${BLUE}To use a different port:${NC}"
echo -e "  ./deploy.sh --port /dev/ttyUSB0"
echo ""
echo -e "${BLUE}Reset the Pico to run the new code:${NC}"
echo -e "  ampy --port $PORT run -n main.py"
echo -e "  or press Ctrl+D in REPL"


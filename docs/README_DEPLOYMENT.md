# 🚀 Deployment Guide

## Available Scripts

### `deploy.sh` - Smart Deployment

Main script that uploads the code to the Pico **only if there are changes**.

#### Basic Usage:
```bash
./deploy.sh
```

#### Options:
```bash
# Force re-upload of ALL files
./deploy.sh --force

# Use a different port
./deploy.sh --port /dev/ttyUSB0

# Combine options (force and use a different port)
./deploy.sh --force --port /dev/ttyACM1
```

#### Environment Variables:
```bash
# Set default port
export PICO_PORT=/dev/ttyUSB0
./deploy.sh
```

## 📝 Recommended Workflow

### 1. Local Development
```bash
# Edit your files in VSCode/Cursor
nano apps/clock.py

# Verify syntax (optional)
python -m py_compile apps/clock.py
```

### 2. Deployment
```bash
# First time - upload everything
./deploy.sh

# Changes later - upload only modified files
./deploy.sh
```

### 3. Testing on the Pico
```bash
# Connect to REPL
screen /dev/ttyACM0 115200
# or
minicom -D /dev/ttyACM0

# In REPL, press Ctrl+D to restart
```

## 🔧 Troubleshooting

### Error: "Device not found"
```bash
# View available ports
ls /dev/ttyACM* /dev/ttyUSB*

# Grant access permissions
sudo chmod 666 /dev/ttyACM0
# or add your user to the dialout group
sudo usermod -a -G dialout $USER
# (requiere logout/login)
```

### Error: "ampy is not installed"
```bash
pip install adafruit-ampy
```

### Reset cache of deployment
```bash
rm .deploy_cache
./deploy.sh --force
```

### View files on the Pico
```bash
ampy --port /dev/ttyACM0 ls
ampy --port /dev/ttyACM0 ls core
ampy --port /dev/ttyACM0 ls apps
```

### Download file from the Pico
```bash
ampy --port /dev/ttyACM0 get main.py
```

### Delete file from the Pico
```bash
ampy --port /dev/ttyACM0 rm main.py
```

## 📊 File Structure on the Pico

After deployment, the Pico will have:

```
/
├── main.py              # Entry point
├── agenda.json          # Persistent data
├── core/
│   ├── __init__.py
│   ├── context.py
│   ├── ui.py
│   └── input.py
└── apps/
    ├── __init__.py
    ├── base.py
    ├── clock.py
    ├── calculator.py
    ├── settings.py
    ├── calendar.py
    ├── contacts.py
    ├── memos.py
    ├── games.py
    └── settime.py
```

## ⚡ Performance Tips

1. **Only upload necessary files**: The script already does this automatically
2. **Use `--force` only when necessary**: Force upload everything, even without changes
3. **Keep the cache**: The `.deploy_cache` file makes the process faster
4. **Test locally first**: Use Python normally to detect syntax errors

## 🐛 Debug

### View real-time logs of the Pico
```bash
# Connect and view output
screen /dev/ttyACM0 115200

# Exit screen: Ctrl+A, then K, then Y
```

### Run code without resetting
```bash
# Run main.py and view output
ampy --port /dev/ttyACM0 run main.py
```

### Restart the Pico
```bash
# Software reset (in REPL)
# Presiona Ctrl+D

# Or import machine
import machine
machine.soft_reset()
```

## 📦 Backup

### Make full backup
```bash
mkdir backup_$(date +%Y%m%d)
ampy --port /dev/ttyACM0 get main.py backup_*/main.py
ampy --port /dev/ttyACM0 get agenda.json backup_*/agenda.json
# ... etc
```



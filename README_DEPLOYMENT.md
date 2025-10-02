# 🚀 Deployment Guide

## Scripts Disponibles

### `deploy.sh` - Deployment Inteligente

Script principal que sube el código al Pico **solo si hay cambios**.

#### Uso Básico:
```bash
./deploy.sh
```

#### Opciones:
```bash
# Forzar re-subida de TODOS los archivos
./deploy.sh --force

# Usar un puerto diferente
./deploy.sh --port /dev/ttyUSB0

# Combinar opciones
./deploy.sh --force --port /dev/ttyACM1
```

#### Variables de Entorno:
```bash
# Configurar puerto por defecto
export PICO_PORT=/dev/ttyUSB0
./deploy.sh
```

## 📝 Flujo de Trabajo Recomendado

### 1. Desarrollo Local
```bash
# Edita tus archivos en VSCode/Cursor
nano apps/clock.py

# Verifica sintaxis (opcional)
python -m py_compile apps/clock.py
```

### 2. Deployment
```bash
# Primera vez - sube todo
./deploy.sh

# Cambios posteriores - solo sube lo modificado
./deploy.sh
```

### 3. Testing en el Pico
```bash
# Conectar a REPL
screen /dev/ttyACM0 115200
# o
minicom -D /dev/ttyACM0

# En REPL, presiona Ctrl+D para reiniciar
```

## 🔧 Troubleshooting

### Error: "Device not found"
```bash
# Ver puertos disponibles
ls /dev/ttyACM* /dev/ttyUSB*

# Dar permisos de acceso
sudo chmod 666 /dev/ttyACM0
# o agregar tu usuario al grupo dialout
sudo usermod -a -G dialout $USER
# (requiere logout/login)
```

### Error: "ampy is not installed"
```bash
pip install adafruit-ampy
```

### Resetear caché de deployment
```bash
rm .deploy_cache
./deploy.sh --force
```

### Ver archivos en el Pico
```bash
ampy --port /dev/ttyACM0 ls
ampy --port /dev/ttyACM0 ls core
ampy --port /dev/ttyACM0 ls apps
```

### Descargar archivo del Pico
```bash
ampy --port /dev/ttyACM0 get main.py
```

### Eliminar archivo del Pico
```bash
ampy --port /dev/ttyACM0 rm main.py
```

## 📊 Estructura de Archivos en el Pico

Después del deployment, el Pico tendrá:

```
/
├── main.py              # Entry point
├── agenda.json          # Datos persistentes
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

## ⚡ Tips de Performance

1. **Solo sube lo necesario**: El script ya hace esto automáticamente
2. **Usa `--force` solo cuando sea necesario**: Forzar sube TODO, incluso sin cambios
3. **Mantén el caché**: El archivo `.deploy_cache` hace el proceso más rápido
4. **Prueba localmente primero**: Usa Python normal para detectar errores de sintaxis

## 🐛 Debug

### Ver logs del Pico en tiempo real
```bash
# Conectar y ver output
screen /dev/ttyACM0 115200

# Salir de screen: Ctrl+A, luego K, luego Y
```

### Ejecutar código sin resetear
```bash
# Ejecutar main.py y ver output
ampy --port /dev/ttyACM0 run main.py
```

### Reiniciar el Pico
```bash
# Software reset (en REPL)
# Presiona Ctrl+D

# O importa machine
import machine
machine.soft_reset()
```

## 📦 Backup

### Hacer backup completo
```bash
mkdir backup_$(date +%Y%m%d)
ampy --port /dev/ttyACM0 get main.py backup_*/main.py
ampy --port /dev/ttyACM0 get agenda.json backup_*/agenda.json
# ... etc
```

## 🔄 Actualización desde Git

Si usas Git:
```bash
git pull
./deploy.sh  # Solo sube archivos modificados
```

## ❓ FAQ

**Q: ¿Cuánto tarda el primer deployment?**  
A: ~30-60 segundos (todos los archivos)

**Q: ¿Y los siguientes?**  
A: 5-10 segundos (solo archivos modificados)

**Q: ¿Puedo usar Thonny en vez de ampy?**  
A: Sí, pero es manual. Este script automatiza todo.

**Q: ¿El caché es seguro?**  
A: Sí, solo guarda hashes MD5 de archivos locales. Si dudas, bórralo.

**Q: ¿Funciona en Windows?**  
A: Necesitas Git Bash o WSL. Los scripts son para Linux/Mac.


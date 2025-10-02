# 🚀 Quick Start Guide

## Primera Vez - Setup

### 1. Instalar ampy (si no lo tienes)
```bash
pip install adafruit-ampy
```

### 2. Dar permisos al puerto serial
```bash
sudo chmod 666 /dev/ttyACM0
# o permanente:
sudo usermod -a -G dialout $USER
# (requiere logout/login)
```

### 3. Verificar conexión
```bash
./pico-utils.sh ls
```

## Desarrollo Diario

### Workflow Simple:
```bash
# 1. Edita tu código
nano apps/clock.py

# 2. Sube cambios (solo archivos modificados)
./deploy.sh

# 3. Reset el Pico
./pico-utils.sh reset
```

## Comandos Útiles

### Deployment
```bash
./deploy.sh              # Sube solo archivos modificados
./deploy.sh --force      # Re-sube TODO
./deploy.sh --port /dev/ttyUSB0  # Usa otro puerto
```

### Utilidades
```bash
./pico-utils.sh ls       # Ver archivos en el Pico
./pico-utils.sh tree     # Ver árbol de archivos
./pico-utils.sh repl     # Conectar a REPL
./pico-utils.sh reset    # Reiniciar Pico
./pico-utils.sh backup   # Backup completo
./pico-utils.sh clean    # Limpiar Pico (⚠️ cuidado!)
```

## Archivos Importantes

- **`deploy.sh`** - Script de deployment inteligente
- **`pico-utils.sh`** - Utilidades para el Pico
- **`main_new.py`** - Entry point modular
- **`README_DEPLOYMENT.md`** - Documentación completa
- **`.deploy_cache`** - Caché de archivos (auto-generado)

## Estructura del Proyecto

```
lcd-gfx/
├── deploy.sh           # ← Script para subir al Pico
├── pico-utils.sh       # ← Utilidades rápidas
├── main_new.py         # ← Entry point
├── core/               # ← Módulos core
│   ├── context.py
│   ├── ui.py
│   └── input.py
└── apps/               # ← Aplicaciones
    ├── base.py
    ├── clock.py
    ├── calculator.py
    └── ...
```

## Tips Rápidos

### Ver logs en tiempo real
```bash
screen /dev/ttyACM0 115200
# Salir: Ctrl+A, luego K, luego Y
```

### Ejecutar sin guardar
```bash
./pico-utils.sh run main_new.py
```

### Resetear caché
```bash
rm .deploy_cache
```

### Backup antes de cambios grandes
```bash
./pico-utils.sh backup
```

## Troubleshooting Rápido

### No encuentra el puerto
```bash
ls /dev/tty{ACM,USB}*
export PICO_PORT=/dev/ttyACM1
```

### Error de permisos
```bash
sudo chmod 666 /dev/ttyACM0
```

### ampy falla
```bash
# Desconecta otros programas (Thonny, screen, etc)
pkill -9 screen
```

### Código no arranca
```bash
# Ver errores en REPL
./pico-utils.sh repl
# Presiona Ctrl+D para reiniciar y ver el error
```

## Flujo Completo - Ejemplo

```bash
# Clonar/editar proyecto
cd /home/manu/dev/micropython/lcd-gfx

# Editar código
nano apps/clock.py

# Verificar sintaxis (opcional)
python -m py_compile apps/clock.py

# Subir al Pico (solo cambios)
./deploy.sh

# Ver lo que se subió
./pico-utils.sh tree

# Conectar y ver funcionando
./pico-utils.sh repl
# Presiona Ctrl+D para ejecutar
```

## ¡Todo Listo! 🎉

Ahora puedes desarrollar rápidamente:
1. Edita código en tu editor favorito
2. Corre `./deploy.sh`
3. Reset con `./pico-utils.sh reset`
4. ¡Prueba!

Para más detalles, lee **`README_DEPLOYMENT.md`**


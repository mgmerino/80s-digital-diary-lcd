# Makefile for MicroPython Pico Development
# Makes common tasks even easier!

.PHONY: help deploy deploy-force clean reset repl backup ls tree

# Default target
help:
	@echo "MicroPython Pico Development - Available Commands:"
	@echo ""
	@echo "  make deploy       - Upload modified files to Pico"
	@echo "  make deploy-force - Upload ALL files to Pico"
	@echo "  make clean        - Remove all files from Pico"
	@echo "  make reset        - Soft reset the Pico"
	@echo "  make repl         - Connect to REPL"
	@echo "  make backup       - Backup files from Pico"
	@echo "  make ls           - List files on Pico"
	@echo "  make tree         - Show file tree on Pico"
	@echo "  make check        - Check Python syntax"
	@echo ""
	@echo "Quick workflow:"
	@echo "  1. Edit your code"
	@echo "  2. make deploy"
	@echo "  3. make reset"
	@echo ""

# Deploy modified files
deploy:
	@./deploy.sh

# Deploy all files (force)
deploy-force:
	@./deploy.sh --force

# Clean Pico
clean:
	@./pico-utils.sh clean

# Reset Pico
reset:
	@./pico-utils.sh reset

# Connect to REPL
repl:
	@./pico-utils.sh repl

# Backup files
backup:
	@./pico-utils.sh backup

# List files
ls:
	@./pico-utils.sh ls

# Show file tree
tree:
	@./pico-utils.sh tree

# Check Python syntax
check:
	@echo "Checking Python syntax..."
	@python -m py_compile main_new.py
	@python -m py_compile core/*.py
	@python -m py_compile apps/*.py
	@echo "✓ All files syntax OK"

# Full workflow: check, deploy, reset
all: check deploy reset
	@echo "✓ Complete deployment done!"


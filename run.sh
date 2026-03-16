#!/bin/bash
# run.sh - Instalacja i uruchomienie eksperymentu EEG2Text
#
# Użycie:
#   ./run.sh                          # Domyślne: approach 2, mock EEG, debug
#   ./run.sh --fullscreen             # Pełny ekran (produkcja)
#   ./run.sh --approach1              # Approach 1 (czytanie + spacja)
#   ./run.sh --words 50 --repeats 10  # Custom parametry
#
# Wszystkie flagi po ./run.sh są przekazywane do main.py

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

VENV_DIR=".venv"

# === KOLORY ===
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}╔═══════════════════════════════════════╗${NC}"
echo -e "${CYAN}║   EEG2Text Single-Word Experiment     ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════╝${NC}"
echo ""

# === PYTHON CHECK ===
if ! command -v python3 &> /dev/null; then
    echo "❌ python3 nie znaleziony. Zainstaluj Python 3.10+."
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION"

# === VENV ===
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}→${NC} Tworzę virtual environment..."
    python3 -m venv "$VENV_DIR"
    echo -e "${GREEN}✓${NC} venv utworzony"
fi

# Aktywuj venv
source "$VENV_DIR/bin/activate"

# === ZALEŻNOŚCI ===
# Sprawdź czy pygame-ce jest zainstalowane
if ! python -c "import pygame" 2>/dev/null; then
    echo -e "${YELLOW}→${NC} Instaluję zależności..."
    pip install --upgrade pip -q
    pip install pygame-ce numpy -q
    echo -e "${GREEN}✓${NC} Zależności zainstalowane"
else
    echo -e "${GREEN}✓${NC} Zależności OK"
fi

# === SPRAWDŹ PLIKI ===
if [ ! -f "zdania.txt" ]; then
    echo "❌ Brak pliku zdania.txt w katalogu projektu!"
    exit 1
fi
echo -e "${GREEN}✓${NC} zdania.txt znaleziony"

# === FOLDERY ===
mkdir -p logs data audio_cache

# === PARSUJ FLAGI ===
# Domyślnie: debug + mock-eeg (chyba że user poda --fullscreen)
DEFAULT_FLAGS="--debug --mock-eeg"
USER_FLAGS="$@"

# Jeśli user podał --fullscreen, usuń --debug
if echo "$USER_FLAGS" | grep -q "\-\-fullscreen"; then
    USER_FLAGS=$(echo "$USER_FLAGS" | sed 's/--fullscreen//g')
    DEFAULT_FLAGS="--mock-eeg"
fi

# Jeśli user podał --real-eeg, usuń --mock-eeg
if echo "$USER_FLAGS" | grep -q "\-\-real-eeg"; then
    USER_FLAGS=$(echo "$USER_FLAGS" | sed 's/--real-eeg//g')
    DEFAULT_FLAGS=$(echo "$DEFAULT_FLAGS" | sed 's/--mock-eeg//g')
fi

FINAL_FLAGS="$DEFAULT_FLAGS $USER_FLAGS"

echo ""
echo -e "${CYAN}Parametry:${NC} $FINAL_FLAGS"
echo -e "${CYAN}Aby zobaczyć wszystkie opcje:${NC} python main.py --help"
echo ""
echo -e "${YELLOW}→${NC} Uruchamiam eksperyment..."
echo ""

# === START ===
python main.py $FINAL_FLAGS

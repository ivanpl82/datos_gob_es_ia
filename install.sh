#!/usr/bin/env bash
set -euo pipefail

# ==============================================================
# install.sh — Instalación de datosgob-cli para OpenCode
# ==============================================================
# Uso:  ./install.sh
#
# Requisitos:  python3 ≥ 3.10, pip, git
# ==============================================================

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_NAME="datosgob"

OPENCODE_CONFIG="${XDG_CONFIG_HOME:-$HOME/.config}/opencode"
OPENCODE_SKILLS="$OPENCODE_CONFIG/skills"
SKILL_DEST="$OPENCODE_SKILLS/$SKILL_NAME"
SKILL_SRC="$PROJECT_DIR/SKILL.md"
REGISTRY_SKILL="$OPENCODE_SKILLS/skill-registry"
REGISTRY_CACHE="$PROJECT_DIR/.atl/skill-registry.md"

# Colores para mensajes
BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

info()  { echo -e "${GREEN}✓${NC} $1"; }
warn()  { echo -e "${YELLOW}⚠${NC} $1"; }
error() { echo -e "${RED}✗${NC} $1"; }
header() { echo -e "\n${BOLD}━━━ $1 ━━━${NC}\n"; }

# --------------------------------------------------------------
# 0. Funciones auxiliares
# --------------------------------------------------------------

# detectar_os — identifica el SO y el gestor de paquetes
detectar_os() {
    # macOS (detecta Homebrew)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        if command -v brew &>/dev/null; then
            echo "macos-brew"
        else
            echo "macos"
        fi
        return
    fi

    # Linux con /etc/os-release
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        case "$ID" in
            ubuntu|debian|linuxmint|pop|elementary|neon|zorin)
                echo "apt" ;;
            fedora|rhel|centos)
                echo "dnf" ;;
            arch|manjaro|endeavouros|artix|arcolinux)
                echo "pacman" ;;
            opensuse*|suse)
                echo "zypper" ;;
            alpine)
                echo "apk" ;;
            void)
                echo "xbps" ;;
            nixos)
                echo "nix" ;;
            *)
                echo "unknown" ;;
        esac
        return
    fi

    # WSL sin os-release
    if uname -r | grep -qi microsoft; then
        echo "apt"
        return
    fi

    echo "unknown"
}

# instalar_pip — instala pip según el gestor de paquetes detectado
instalar_pip() {
    local pkg_manager="$1"

    # Casos donde no necesitamos sudo
    case "$pkg_manager" in
        macos-brew)
            warn "Instalando python via Homebrew (incluye pip)..."
            brew install python
            return $?
            ;;
        nix)
            warn "Instalando python3-pip via nix..."
            nix profile install nixpkgs#python3Packages.pip
            return $?
            ;;
    esac

    # El resto necesita privilegios administrativos
    if ! command -v sudo &>/dev/null; then
        error "Se necesita sudo pero no está disponible en este sistema."
        error "Ejecutá manualmente el comando correspondiente según tu SO:"
        case "$pkg_manager" in
            apt)    echo "  sudo apt update && sudo apt install -y python3-pip python3-venv" ;;
            dnf)    echo "  sudo dnf install -y python3-pip" ;;
            pacman) echo "  sudo pacman -S python-pip" ;;
            zypper) echo "  sudo zypper install -y python3-pip" ;;
            apk)    echo "  sudo apk add py3-pip" ;;
            xbps)   echo "  sudo xbps-install -S python3-pip" ;;
            *)      echo "  python3 -m ensurepip --upgrade" ;;
        esac
        return 1
    fi

    warn "Se necesita sudo para instalar pip..."

    case "$pkg_manager" in
        apt)
            sudo apt update -qq && sudo apt install -y python3-pip python3-venv
            ;;
        dnf)
            sudo dnf install -y python3-pip
            ;;
        pacman)
            sudo pacman -S --noconfirm python-pip
            ;;
        zypper)
            sudo zypper install -y python3-pip
            ;;
        apk)
            sudo apk add py3-pip
            ;;
        xbps)
            sudo xbps-install -S python3-pip
            ;;
        *)
            # Fallback: ensurepip (funciona en Python ≥ 3.4)
            warn "Gestor de paquetes no reconocido, intentando ensurepip..."
            python3 -m ensurepip --upgrade
            return $?
            ;;
    esac
}

# --------------------------------------------------------------
# 1. Validar requisitos
# --------------------------------------------------------------
header "Validando requisitos"

if ! command -v python3 &>/dev/null; then
    error "python3 no está instalado. Instálalo primero (≥ 3.10)."
    exit 1
fi

PY_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
if awk -v ver="$PY_VERSION" 'BEGIN { exit !(ver < 3.10) }'; then
    error "Se necesita Python ≥ 3.10 (tienes $PY_VERSION)."
    exit 1
fi
info "Python $PY_VERSION detectado"

if ! python3 -m pip --version &>/dev/null; then
    warn "pip no está instalado. Detectando SO para instalarlo automáticamente..."

    PKG_MANAGER="$(detectar_os)"
    info "Sistema detectado: $PKG_MANAGER"

    if ! instalar_pip "$PKG_MANAGER"; then
        error "No se pudo instalar pip automáticamente."
        error "Instalalo manualmente y volvé a ejecutar este script."
        info "Alternativa rápida: usar un virtualenv manual"
        echo
        echo "  python3 -m venv .venv"
        echo "  source .venv/bin/activate"
        echo "  pip install -e ."
        echo
        exit 1
    fi

    # Verificar que ahora funcione
    if ! python3 -m pip --version &>/dev/null; then
        error "pip sigue sin estar disponible después de la instalación."
        exit 1
    fi
    info "pip instalado correctamente"
else
    info "pip disponible"
fi

if [ ! -f "$SKILL_SRC" ]; then
    error "No se encuentra SKILL.md en $SKILL_SRC"
    exit 1
fi
info "Skill source encontrada"

# --------------------------------------------------------------
# 2. Instalar paquete Python (en virtualenv por PEP 668)
# --------------------------------------------------------------
header "Instalando paquete Python"

VENV_DIR="$PROJECT_DIR/.venv"
VENV_PYTHON="$VENV_DIR/bin/python3"
VENV_PIP="$VENV_DIR/bin/pip"
VENV_CLI="$VENV_DIR/bin/datosgob"

if [ ! -f "$VENV_PYTHON" ]; then
    info "Creando virtualenv en $VENV_DIR..."
    python3 -m venv "$VENV_DIR" --clear
fi

info "Instalando datosgob-cli en modo editable..."
"$VENV_PIP" install -e "$PROJECT_DIR" --quiet
info "Paquete instalado: datosgob-cli"

# Crear symlink en ~/.local/bin para acceso global
LOCAL_BIN="${HOME}/.local/bin"
SYMLINK_TARGET="$LOCAL_BIN/datosgob"
mkdir -p "$LOCAL_BIN"

if [ -L "$SYMLINK_TARGET" ] && [ "$(readlink -f "$SYMLINK_TARGET")" = "$(readlink -f "$VENV_CLI")" ]; then
    info "Symlink ~/.local/bin/datosgob ya existe"
elif [ -f "$SYMLINK_TARGET" ]; then
    warn "~/.local/bin/datosgob ya existe y no es un symlink — no se sobreescribe"
else
    ln -s "$VENV_CLI" "$SYMLINK_TARGET"
    info "Symlink creado: ~/.local/bin/datosgob → .venv/bin/datosgob"
fi

# Verificar que el CLI funciona
if "$VENV_CLI" --help &>/dev/null; then
    info "CLI responde correctamente"
else
    error "El CLI no responde desde el virtualenv."
    exit 1
fi

# --------------------------------------------------------------
# 3. Instalar skill en OpenCode
# --------------------------------------------------------------
header "Instalando skill en OpenCode"

if [ ! -d "$OPENCODE_CONFIG" ]; then
    warn "No se encontró $OPENCODE_CONFIG — creando directorio"
    mkdir -p "$OPENCODE_CONFIG"
fi

mkdir -p "$SKILL_DEST"

if [ -f "$SKILL_DEST/SKILL.md" ]; then
    if cmp -s "$SKILL_SRC" "$SKILL_DEST/SKILL.md"; then
        info "Skill ya actualizada — sin cambios en $SKILL_DEST/SKILL.md"
    else
        warn "Cambios detectados — actualizando skill en $SKILL_DEST/SKILL.md..."
        cp "$SKILL_SRC" "$SKILL_DEST/SKILL.md"
        info "Skill actualizada"
    fi
else
    cp "$SKILL_SRC" "$SKILL_DEST/SKILL.md"
    info "Skill instalada en $SKILL_DEST/SKILL.md"
fi

# --------------------------------------------------------------
# 4. Actualizar registro de skills
# --------------------------------------------------------------
header "Actualizando registro de skills"

if [ -f "$REGISTRY_SKILL/SKILL.md" ]; then
    info "Ejecutando skill-registry..."
    # Registro manual en el cache
    mkdir -p "$(dirname "$REGISTRY_CACHE")"
    cat > "$REGISTRY_CACHE" <<-REGEOF
# Skill Registry — datosgob

| Skill | Trigger | Scope | Path |
|-------|---------|-------|------|
| datosgob | datos.gob.es, datos abiertos España, datasets gobierno | global | $SKILL_DEST/SKILL.md |
REGEOF
    info "Registro actualizado en $REGISTRY_CACHE"
else
    warn "skill-registry no encontrado — el registro se actualizará al próximo scan"
    # Aún así escribir el cache local
    mkdir -p "$(dirname "$REGISTRY_CACHE")"
    cat > "$REGISTRY_CACHE" <<-REGEOF
# Skill Registry — datosgob

| Skill | Trigger | Scope | Path |
|-------|---------|-------|------|
| datosgob | datos.gob.es, datos abiertos España, datasets gobierno | project | $SKILL_DEST/SKILL.md |
REGEOF
    info "Registro local escrito en $REGISTRY_CACHE"
fi

# --------------------------------------------------------------
# 5. Resumen final
# --------------------------------------------------------------
header "Instalación completa"

echo -e "  ${BOLD}Virtualenv:${NC} $VENV_DIR"
echo -e "  ${BOLD}CLI:${NC}       $SYMLINK_TARGET"
echo -e "  ${BOLD}Skill:${NC}     $SKILL_DEST/SKILL.md"
echo -e "  ${BOLD}Docs:${NC}      $PROJECT_DIR/README.md"
echo

# Verificar que ~/.local/bin está en PATH
case ":$PATH:" in
    *:"$LOCAL_BIN":*)
        info "~/.local/bin está en PATH — podés usar 'datosgob' directamente"
        ;;
    *)
        warn "~/.local/bin NO está en PATH. Agregalo a tu shell:"
        echo "  echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.bashrc"
        echo "  source ~/.bashrc"
        echo
        echo "Mientras tanto, usá el CLI desde el virtualenv:"
        echo "  $VENV_CLI --help"
        ;;
esac

echo
echo -e "Para probar:"
echo -e "  ${BOLD}datosgob --help${NC}"
echo -e "  ${BOLD}datosgob dataset list --theme salud${NC}"
echo
echo -e "La skill se cargará automáticamente la próxima vez que"
echo -e "inicies OpenCode."

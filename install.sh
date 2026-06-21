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
    error "pip no está instalado. Ejecuta: python3 -m ensurepip --upgrade"
    exit 1
fi
info "pip disponible"

if [ ! -f "$SKILL_SRC" ]; then
    error "No se encuentra SKILL.md en $SKILL_SRC"
    exit 1
fi
info "Skill source encontrada"

# --------------------------------------------------------------
# 2. Instalar paquete Python
# --------------------------------------------------------------
header "Instalando paquete Python"

info "Instalando datosgob-cli en modo editable..."
python3 -m pip install -e "$PROJECT_DIR" --quiet
info "Paquete instalado: datosgob-cli"

# Verificar que el CLI funciona
if python3 -m datosgob_cli.cli --help &>/dev/null; then
    info "CLI responde correctamente"
else
    # Fallback: probar con PYTHONPATH
    if PYTHONPATH="$PROJECT_DIR/src" python3 -m datosgob_cli.cli --help &>/dev/null; then
        warn "CLI funciona con PYTHONPATH — revisa la instalación pip"
    else
        error "El CLI no responde. Revisa la instalación."
        exit 1
    fi
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
    warn "Sobrescribiendo skill existente en $SKILL_DEST/SKILL.md"
fi

cp "$SKILL_SRC" "$SKILL_DEST/SKILL.md"
info "Skill instalada en $SKILL_DEST/SKILL.md"

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

echo -e "  ${BOLD}Skill:${NC}     $SKILL_DEST/SKILL.md"
echo -e "  ${BOLD}CLI:${NC}       datosgob (comando global)"
echo -e "  ${BOLD}Docs:${NC}      $PROJECT_DIR/README.md"
echo
echo -e "Para probar:"
echo -e "  ${BOLD}datosgob --help${NC}"
echo -e "  ${BOLD}datosgob dataset list --theme salud${NC}"
echo
echo -e "La skill se cargará automáticamente la próxima vez que"
echo -e "inicies OpenCode."

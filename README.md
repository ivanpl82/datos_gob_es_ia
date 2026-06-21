# datosgob-cli

CLI para consumir la API de datos abiertos del gobierno de España ([datos.gob.es](https://datos.gob.es/es/apidata)) desde la terminal y desde agentes OpenCode.

## ¿Qué hace?

Consulta en vivo el catálogo de datos abiertos español — datasets, distribuciones, publicadores, temáticas y coberturas geográficas — sin necesidad de descargar nada ni tener servidores corriendo.

La API oficial expone más de 25 endpoints con toda la información pública del gobierno central, comunidades autónomas, diputaciones y ayuntamientos. Este script los envuelve en una CLI coherente.

## Instalación

### Requisitos

- Python ≥ 3.10
- pip
- OpenCode (para usar como skill)

### Rápida

```bash
git clone https://github.com/ivanpl82/datos_gob_es_ia.git
cd datos_gob_es_ia
chmod +x install.sh
./install.sh
```

El script:
1. Instala el paquete Python en modo editable
2. Copia la skill en `~/.config/opencode/skills/datosgob/`
3. Actualiza el registro de skills

### Manual

```bash
pip install -e .
```

Luego copia `SKILL.md` a `~/.config/opencode/skills/datosgob/SKILL.md` para que OpenCode pueda usarlo.

## Uso

```text
datosgob <comando> <subcomando> [OPCIONES]
```

### Comandos

| Comando | Subcomando | Descripción |
|---------|------------|-------------|
| `dataset` | `list` | Lista datasets con filtros |
| `distribution` | `list` | Lista distribuciones de recursos |
| `publisher` | `list` / `get <id>` | Lista o busca publicadores |
| `theme` | `list` | Lista temáticas disponibles |
| `spatial` | `list` | Lista coberturas geográficas |
| `nti` | `list` | Lista NTI (taxonomías y territorios) |

### Filtros disponibles

| Comando | Filtros |
|---------|---------|
| `dataset list` | `--theme`, `--publisher`, `--keyword`, `--spatial`, `--resource-format`, `--modified-begin/end`, `--issued-begin/end` |
| `distribution list` | `--by-dataset`, `--by-format` |
| `publisher` | `--id` |
| `nti list` | `--sector`, `--territory` |

### Opciones globales

| Opción | Valores | Defecto | Descripción |
|--------|---------|---------|-------------|
| `--format` | `json`, `csv` | `json` | Formato de salida |
| `--pandas` | flag | `false` | Salida como DataFrame (JSON serializado) |
| `--page-size` | 1–50 | 10 | Items por página |

### Ejemplos

```bash
# Todos los datasets de salud
datosgob dataset list --theme salud

# En CSV
datosgob dataset list --theme salud --format csv

# Como DataFrame para análisis
datosgob dataset list --theme salud --pandas

# Datasets de un publicador concreto
datosgob dataset list --publisher A16003011

# Datasets actualizados en 2025
datosgob dataset list --modified-begin 2025-01-01T00:00Z --modified-end 2025-12-31T23:59Z

# Distribuciones en CSV de un dataset
datosgob distribution list --by-dataset mi-dataset-id --format csv

# Listar temáticas
datosgob theme list

# Listar provincias (NTI)
datosgob nti list --territory province
```

## Como skill de OpenCode

Cuando la skill está instalada y OpenCode se reinicia, el agente puede usar `datosgob` automáticamente cuando detecte consultas como:

- _"Dame los datos de salud del gobierno de España"_
- _"¿Qué datasets hay sobre medio ambiente?"_
- _"Pon en un mapa los datos de..."_
- _"Haz un análisis estadístico con los datos de empleo"_
- _"Busca datasets actualizados en 2025"_

La skill se activa con palabras clave como **datos.gob.es**, **datos abiertos España**, **datasets gobierno**, o **datosgob**.

## Arquitectura

```
src/datosgob_cli/
├── client.py       → requests.Session + paginación (generador hasta next)
├── formatters.py   → format_json(), format_csv(), format_pandas()
├── cli.py          → click.Group (entry point)
└── commands/
    ├── dataset.py
    ├── distribution.py
    ├── publisher.py
    ├── theme.py
    ├── spatial.py
    └── nti.py
```

## API de datos.gob.es

La API oficial utiliza **linked-data-api v0.2** sobre RDF/DCAT-AP.

| Característica | Detalle |
|----------------|---------|
| Base URL | `https://datos.gob.es/apidata/` |
| Autenticación | No requiere |
| Paginación | `_page`, `_pageSize` (máx 50) |
| Total | Sin `totalCount` — se itera hasta que falte `next` |
| Formatos | JSON, XML, RDF, Turtle, CSV |
| Rate limiting | No documentado — se aplica delay de 0.5s entre páginas |

## Desarrollo

```bash
# Entorno virtual
python3 -m venv .venv && source .venv/bin/activate

# Dependencias de desarrollo
pip install -e ".[dev]"

# Tests
python3 -m pytest tests/ -v

# Linter
ruff check src/
ruff format src/
```

## Licencia

MIT

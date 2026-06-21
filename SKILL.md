# SKILL: datosgob — CLI para la API de datos.gob.es

## Metadata
- **name**: `datosgob`
- **version**: `0.1.0`
- **author**: comunidad OpenCode

## Trigger

El agente invoca este comando cuando el usuario menciona **datos del gobierno español**, **datos.gob.es**, **datos abiertos de España**, o cualquier variante de **datosgob**, **datos.gob**, **datos abiertos**.

También se activa con consultas que mencionan **datasets**, **distribuciones**, **publicadores**, **temas**, **coberturas geográficas**, **NTI** o **filtros por categoría** dentro del catálogo de datos abiertos de España.

## Uso

```
datosgob <comando> <subcomando> [OPCIONES]
```

### Comandos disponibles

| Comando | Subcomando | Descripción |
|---------|------------|-------------|
| `dataset` | `list` | Lista datasets con filtros opcionales |
| `distribution` | `list` | Lista distribuciones de recursos |
| `publisher` | `list` / `get <id>` | Lista o busca publicadores |
| `theme` | `list` | Lista temas/taxonomías |
| `spatial` | `list` | Lista coberturas geográficas |
| `nti` | `list` | Lista NTI (Núcleos de Intervención) |

### Opciones globales

| Opción | Tipo | Por defecto | Descripción |
|--------|------|------------|-------------|
| `--format` | `json` / `csv` | `json` | Formato de salida |
| `--pandas` | flag | `false` | Salida como DataFrame pandas (JSON) |
| `--page-size` | int (1–50) | 10 | Número de items por página |

### Ejemplos

```shell
# Listar datasets del tema salud
datosgob dataset list --theme salud

# Mismo en CSV
datosgob dataset list --theme salud --format csv

# Listar publicadores como DataFrame pandas
datosgob publisher list --pandas

# Obtener un publicador por ID
datosgob publisher get /id/12345

# Salida JSON
datosgob theme list --format json
```

## Salida esperada

Todas las respuestas son JSON estructurado con `items` (lista de objetos) y metadatos de paginación.

Los campos `next` y `page` indican si hay más resultados disponibles.

## Notas técnicas

- **API**: [linked-data-api v0.2](https://datos.gob.es/apidata) — compatible con DCAT-AP.
- **Sin autenticación**: la API es pública, sin API key.
- **Paginación**: el cliente recorre páginas hasta que falte el campo `next`.
- **Rate limiting**: respeta un delay de 0.5s entre peticiones.
- **Timeouts**: por defecto 10s, configurables.
- **Formato pandas**: requiere `pandas>=2.0` instalado en el entorno.
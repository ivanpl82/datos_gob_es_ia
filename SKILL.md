---
name: datosgob
description: "CLI para la API de datos.gob.es. Trigger: datos del gobierno español, datos.gob.es, datos abiertos de España, datasets, distribuciones, publicadores, temas, coberturas geográficas, NTI."
license: MIT
metadata:
  author: ivanpl82
  version: "0.2.0"
---

# SKILL: datosgob — CLI para la API de datos.gob.es

## Metadata
- **name**: `datosgob`
- **version**: `0.2.0`
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
| `dataset` | `list` | Lista datasets con filtros opcionales por campos DCAT |
| `dataset` | `get <identifier>` | Obtiene un dataset individual por su UUID (`identifier`) |
| `distribution` | `list` | Lista distribuciones de recursos |
| `publisher` | `list` / `get <id>` | Lista o busca publicadores |
| `theme` | `list` | Lista temas/taxonomías |
| `spatial` | -- | **NO DISPONIBLE** — el endpoint devuelve error 500 |
| `nti` | `list` | Lista NTI (Núcleos de Intervención) |

### Opciones globales

| Opción | Tipo | Por defecto | Descripción |
|--------|------|------------|-------------|
| `--format` | `json` / `csv` | `json` | Formato de salida |
| `--pandas` | flag | `false` | Salida como DataFrame pandas (JSON) |
| `--page-size` | int (1–50) | 10 | Número de items por página |

### Ejemplos

```shell
# Listar datasets del tema salud (página 0, 10 resultados)
datosgob dataset list --theme salud

# Obtener un dataset por identifier (UUID)
datosgob dataset get b0da07b8-a123-4abc-9def-0123456789ab

# Listar publicadores como DataFrame pandas
datosgob publisher list --pandas

# Obtener un publicador por ID
datosgob publisher get /id/12345

# Salida JSON
datosgob theme list --format json
```

## Comportamiento detallado

### URL base de la API

La URL real de la API es:

```
https://datos.gob.es/apidata/catalog/dataset.json?{params}
```

**Importante**: la extensión `.json` es obligatoria para el endpoint de datasets. Sin ella la API responde con HTML en vez de JSON.

### Parámetros de filtrado disponibles (dataset list)

La API **no** soporta búsqueda por texto libre. No existe un parámetro `q` ni `_search`. El único método para filtrar datasets es a través de propiedades concretas del modelo DCAT-AP:

| Parámetro | Descripción | Ejemplo |
|-----------|-------------|---------|
| `theme` | Filtra por tema (URI o etiqueta) | `theme=http://datos.gob.es/kos/sector-publico/sector/salud` |
| `publisher` | Filtra por publicador | `publisher=/id/12345` |
| `keyword` | Filtra por palabra clave | `keyword=salud` |
| `spatial` | Filtra por URI geográfica | `spatial=http://datos.gob.es/recurso/sector-publico/territorio/Autonomia/Andalucia` |
| `format` | Filtra por formato del recurso | `format=text/csv` |
| `modified` | Rango de modificación | `modified=>=2024-01-01,<=2024-12-31` |
| `issued` | Rango de publicación | `issued=>=2024-01-01` |

**Limitaciones conocidas**:
- El filtro `q` (texto libre) **no existe**. La API lo rechaza con error "unrecognised short name".
- El filtro `_search` **no funciona**. Devuelve 0 resultados siempre.
- El filtro `spatial` **no es fiable**: la mayoría de datasets usan URIs de `idee.es` en vez del patrón de datos.gob.es. Filtrar por `spatial=...` puede devolver 0 resultados aunque existan datasets de esa región.

### Búsqueda por contenido

Dado que la API **no expone búsqueda por texto libre**, para encontrar datasets por palabras clave hay que iterar páginas con `_page=N` y `_pageSize=50` (máximo permitido), y filtrar localmente los campos `title`, `description`, `keyword`, `publisher`.

### Paginación

| Propiedad | Valor |
|-----------|-------|
| `_page` | Empieza en **0** (no en 1) |
| `_pageSize` | Máximo **50** items por página |
| Campo `next` | Cuando falta, no hay más resultados |
| Límite real | La API tiene ~2500 datasets totales (~50 páginas a 50 items) |

### Estructura de la respuesta JSON

La API devuelve un objeto con esta estructura:

```json
{
  "result": {
    "items": [
      {
        "identifier": [{"_value": "b0da07b8-...", "_lang": "es"}],
        "title": [
          {"_value": "Datos de salud pública en Andalucía", "_lang": "es"}
        ],
        "description": [
          {"_value": "Conjunto de datos sobre ...", "_lang": "es"}
        ],
        "keyword": [
          {"_value": "salud", "_lang": "es"},
          {"_value": "Andalucía", "_lang": "es"}
        ],
        "publisher": {"_value": "/id/12345", "_lang": "es"},
        "spatial": [
          {"_value": "http://idee.es/...", "_lang": "es"}
        ],
        "_about": "b0da07b8-a123-4abc-9def-0123456789ab"
      }
    ],
    "itemsPerPage": 50,
    "page": 0,
    "startIndex": 0
  }
}
```

**Importante**: `title`, `description`, y `keyword` son **listas de objetos**, no strings planas. Cada objeto tiene `_value` (texto) y `_lang` (idioma). Para extraer el texto en Python:

```python
title_text = title[0].get("_value", "") if isinstance(title, list) and title else ""
desc_text = description[0].get("_value", "") if isinstance(description, list) and description else ""
keywords = [k.get("_value", "") for k in keyword if isinstance(k, dict)]
```

### `dataset get` — Obtener dataset individual

Para obtener un dataset específico se necesita su `identifier` (UUID). El identifier aparece en el campo `identifier` (lista de objetos con `_value`) o en `_about` del item.

```
GET https://datos.gob.es/apidata/catalog/dataset/{identifier}.json
```

Ejemplo:

```shell
datosgob dataset get b0da07b8-a123-4abc-9def-0123456789ab
```

### Endpoint `/spatial`

El endpoint `https://datos.gob.es/apidata/catalog/spatial` devuelve **Internal Server Error (500)**. No está operativo. El comando `datosgob spatial list` muestra este error explícitamente.

### URIs de comunidades autónomas verificadas

Patrón confirmado:
```
http://datos.gob.es/recurso/sector-publico/territorio/Autonomia/{Nombre}
```

**Nota**: se usa `Autonomia`, no `ComunidadAutonoma`. Comunidades encontradas en datasets reales: Aragon, Castilla-Leon, Cataluna, Region-Murcia. La mayoría de comunidades autónomas **no aparecen** en las URIs de datasets; el sistema de cobertura geográfica usa predominantemente URIs de `idee.es`.

## Salida esperada

Todas las respuestas son JSON estructurado con `result.items` (lista de objetos con formato linked-data-api) y metadatos de paginación en `result` (`itemsPerPage`, `page`, `startIndex`).

El campo `next` en la raíz del JSON indica si hay más páginas disponibles. Cuando falta `next`, no hay más resultados.

## Notas técnicas

- **API**: [linked-data-api v0.2](https://datos.gob.es/apidata) — compatible con DCAT-AP.
- **URL base**: `https://datos.gob.es/apidata` (los endpoints específicos pueden requerir extensión `.json`).
- **Sin autenticación**: la API es pública, sin API key.
- **Sin búsqueda por texto**: no existe `q`, `_search` ni equivalente. Solo filtros por campo DCAT.
- **Paginación**: `_page` empieza en 0, `_pageSize` máximo 50.
- **`spatial`**: no es un filtro fiable. El endpoint dedicado devuelve error 500.
- **Rate limiting**: respeta un delay de 0.5s entre peticiones.
- **Timeouts**: por defecto 10s, configurables.
- **Formato pandas**: requiere `pandas>=2.0` instalado en el entorno.
- **Límite real**: la API tiene ~2500 datasets (~50 páginas a 50 items).
- **`title`/`description`/`keyword`**: son listas de `{"_value": string, "_lang": string}`, no strings planas.

### Limitaciones conocidas (resumen)

1. No hay búsqueda por texto libre (`q`, `_search` no funcionan).
2. `spatial` no es fiable como filtro geográfico; la mayoría de datasets usan URIs de `idee.es`.
3. El endpoint `/spatial` devuelve error 500.
4. Pocos datasets tienen URIs de comunidad autónoma en datos.gob.es.
5. Para búsqueda regional específica (ej. Andalucía), redirigir al usuario al portal CKAN de la Junta de Andalucía.
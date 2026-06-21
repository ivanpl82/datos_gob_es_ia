## Exploration: API datos.gob.es -- integracion con OpenCode

### Current State
Proyecto `datos_gob_es_ia` es **greenfield** - solo existe `README.md` con descripcion de 1 linea y `openspec/config.yaml` generado por `sdd-init`. No hay codigo, tests, ni dependencias instaladas. El `.gitignore` es template Python estandar.

### API datos.gob.es - descubrimiento

**URL base**: `http://datos.gob.es/apidata/catalog/`
**Base semantica**: `http://datos.gob.es/apidata/` (catalogo de datos) y `http://datos.gob.es/apidata/nti/` (taxonomia NTI)

**Formato**: Linked Data API (LDAPI) v0.2 sobre RDF/DCAT-AP. Respuesta por defecto JSON.
**Sin autenticacion**: consultas publicas, sin API key ni token.
**Formatos disponibles**: JSON, XML, RDF, TTL (Turtle), CSV - via `Accept` header o extension de URL (`.json`, `.xml`, `.rdf`, `.ttl`, `.csv`).

**Endpoints principales**:
- `/catalog/dataset` - todos los datasets (paginado)
- `/catalog/dataset/{id}` - un dataset por URI
- `/catalog/dataset/title/{title}` - busqueda por titulo
- `/catalog/dataset/publisher/{id}` - por publicador
- `/catalog/dataset/theme/{id}` - por tematica
- `/catalog/dataset/format/{format}` - por formato de distribucion
- `/catalog/dataset/keyword/{keyword}` - por keyword
- `/catalog/dataset/spatial/{spatialWord1}/{spatialWord2}` - por ambito geografico
- `/catalog/dataset/modified/begin/{begin}/end/{end}` - por rango de fechas

**Paginacion**:
- `_pageSize` - numero por pagina (max 50)
- `_page` - pagina (0-indexed)
- `_sort` - ordenacion (`-issued`, `title`, etc.)

**Otros endpoints**:
- `/catalog/distribution` - distribuciones
- `/catalog/publisher` - listado de publicadores
- `/catalog/spatial` - coberturas geograficas
- `/catalog/theme` - categorias/tematicas
- `/nti/public-sector/{id}` - taxonomia NTI de sectores
- `/nti/territory/Province/{id}`, `/nti/territory/Autonomous-region/{id}` - provincias/CCAA

**Ejemplo de respuesta** (JSON):
```json
{
  "format": "linked-data-api",
  "version": "0.2",
  "result": {
    "items": [ { /* dataset con _about, title, description, publisher, theme, distribution... */ } ],
    "itemsPerPage": 2,
    "page": 0,
    "next": "http://datos.gob.es/apidata/catalog/dataset.json?_page=1"
  }
}
```

### Affected Areas
- `openspec/config.yaml` - ya existe, describe proyecto como greenfield, stack: Python 3, pip
- `openspec/explore.md` - este archivo (descubrimientos de API)
- Potencial: `src/`, `tests/`, `pyproject.toml` - todo por crear

### Approaches

1. **Skill (SKILL.md)** - instrucciones + contexto para el LLM, no codigo ejecutable
   - **Pros**: Zero infraestructura, nulo mantenimiento de servidor, se integra con el flujo de OpenCode existente, no necesita instalar Python, perfecto para consultas exploratorias
   - **Cons**: No puede hacer llamadas HTTP reales, solo da contexto al LLM sobre como consumir la API, no automatiza descargas ni transformaciones
   - **Effort**: Low (escribir markdown estructurado)

2. **Tool/MCP (Model Context Protocol)** - servidor Python que expone herramientas al LLM
   - **Pros**: Puede ejecutar consultas reales en runtime, parsear respuestas, cachear resultados - interaccion dinamica con datos reales
   - **Cons**: Requiere infraestructura (servidor asyncio, protocolo MCP, puerto), mas complejo de mantener, necesita instalacion de dependencias Python, no es el modelo nativo de OpenCode (que usa skills markdown, no MCP)
   - **Effort**: High (servidor MCP + herramientas + tests + despliegue)
   - **Nota**: OpenCode actual no expone un MCP server nativo. Las skills son markdown. Si se busca MCP, habria que crear el server aparte.

3. **Script/Bash (CLI)** - comando directo que descarga y parsea datos
   - **Pros**: Simple de implementar (Python + requests + argparse), ejecutable desde terminal o pipeline CI/CD, script unico y autonomo
   - **Cons**: Solo descarga datos estaticos, no ofrece consulta dinamica al LLM (salvo que el script devuelva datos que el LLM lea como contexto), no escala a multiples consultas sin cacheo
   - **Effort**: Medium (script Python + pytest + CI)

### Recommendation

**Skill-first approach** con un script de soporte opcional:

1. Crear una `SKILL.md` que documente la API de datos.gob.es (endpoints, parametros, formato de respuesta) para que el LLM sepa como construir consultas y parsear respuestas. Esto es lo que mejor se alinea con la arquitectura de OpenCode.

2. Opcional: un script Python CLI (`datosgob.py`) que haga consultas reales a la API, descargue datasets en JSON/CSV, y los devuelva formateados. Esto le da al proyecto valor real (poder bajar datos) y sirve como herramienta para el LLM cuando necesita datos frescos.

**Razon**: El proyecto es greenfield. Lo mas simple y mantenible es una skill documentada. Si despues se necesita automatizacion, el script CLI es el paso natural sin re-architecturar.

### Risks
- La API de datos.gob.es usa formato `linked-data-api` (no REST estandar) - las URIs internas (`_about`, `definition`) son relativas a la ontologia. No hay OpenAPI/Swagger publico.
- Sin autenticacion, pero la API puede rate-limit sin aviso. Recomendacion: usar `_pageSize` bajo (10-20) y respetar `Retry-After` si aparece.
- No hay un endpoint de busqueda textual/full-text - solo por `title` exacto o `keyword` exacto. Para busqueda semantica hay que parsear los resultados de paginacion completa o usar SPARQL.

### Ready for Proposal
Si. Toda la info esta disponible. El siguiente paso es `sdd-propose` para definir que se construye exactamente.

## Preguntas de clarificacion (3-5)

1. **Que tipo de integracion queres?** - una SKILL.md que le de contexto al LLM sobre como usar la API? O un script real que descargue y procese datos? O las dos cosas?

2. **Que datos te interesan especificamente?** - cualquier dataset abierto? categorias tematicas (salud, medio ambiente, economia)? filtro por publicador? por fecha? necesitas datos en CSV o JSON?

3. **Necesitas consultas en tiempo real (mientras chateas con el LLM) o datos precargados/estaticos?** - Si es tiempo real, un script Python que el LLM invoque es mejor. Si es contexto estatico, una skill alcanza.

4. **Hay algun stack especifico de Python que prefieras?** - `uv`/`pip`/`poetry`? pytest si o si? ruff o flake8? El `.gitignore` cubre todos, pero la decision de empaquetado es tuya.

5. **Queres que el script descargue datasets completos o solo explore el catalogo (metadatos)?** - Los datasets pueden tener distribuciones grandes. Streaming? Lazy loading? O solo metadatos del catalogo basico?
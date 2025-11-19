# NewsFeeder

## Descripcion general
NewsFeeder automatiza la recoleccion, limpieza y enriquecimiento de articulos de noticias para construir un repositorio listo para analitica. El pipeline ingiere noticias desde fuentes publicas (BBC, CNN, Wall Street Journal, Al Jazeera y NewsAPI), elimina duplicados, resume textos extensos y clasifica cada articulo por sentimiento y categoria tematica antes de almacenarlo en MongoDB.

## Caracteristicas clave
- Ingesta hibrida: scrapers dedicados para medios concretos y conectores basados en NewsAPI.
- Deduplicacion mediante `link_pool` para impedir reprocesar URLs ya tratadas.
- Resumenes extractivos con modelos BART y clasificacion Zero-Shot para etiquetar temas.
- Analisis de sentimiento con DistilBERT ajustado a SST-2.
- Registro de metadatos operativos (volumen procesado, distribuciones por tema y sentimiento, marcas de tiempo del lote).
- Descarga y cacheo offline de modelos de Transformers para ejecuciones sin red.

## Arquitectura del pipeline
1. **Ingesta (`ingest/custom_scrapers.py`, `ingest/news_api_scrapper.py`):** recolecta articulos y solo conserva los que no han sido procesados previamente (`LinkPoolRepository`). Para cada URL se obtiene el cuerpo con `trafilatura`.
2. **Clasificacion (`ingest/classifier.py`):** genera resenas con `ingest/summarizer.py`, aplica los pipelines de sentimiento y zero-shot, y escribe los resultados en `articles`.
3. **Persistencia (`lib/repositories/*.py`):** repositorios orientados a colecciones encapsulan las operaciones CRUD para `articles`, `clean_articles`, `summaries`, `daily_trends`, `metadata` y `link_pool`.
4. **Monitoreo (`outputs/main.py`):** utilidades de consola para inspeccionar colecciones y depurar la instancia de MongoDB.

## Dependencias principales
- Scraping: `requests`, `trafilatura`, `beautifulsoup4`, `feedparser`, `lxml`.
- ML/NLP: `transformers`, `torch`, `safetensors`.
- Persistencia: `pymongo`, `python-dotenv`.
- CLI y soporte: `typer`, `rich`, `tqdm`.
Todas las versiones recomendadas se listan en `requirements.txt`.

## Requisitos previos
- Python 3.10 o superior.
- MongoDB accesible (local o remoto) y credenciales con permisos de lectura/escritura.
- Cuenta de NewsAPI para obtener `NEWSAPI_KEY` (solo necesaria si se habilita la ingesta desde NewsAPI).
- Espacio en disco para almacenar los modelos de HuggingFace (aprox. 3 GB por defecto).

## Preparacion del entorno
```bash
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```
Cree un archivo `.env` en la raiz (el repositorio ya incluye un ejemplo). Variables soportadas:

| Variable | Obligatoria | Descripcion |
|----------|-------------|-------------|
| `MONGO_URI` | Si | URI de conexion para MongoDB. |
| `MONGODB_DB` | Si | Nombre de la base de datos donde se crean las colecciones. |
| `APP_NAME` | No | Etiqueta opcional para identificar la aplicacion en MongoDB (por defecto `trend-app`). |
| `NEWSAPI_KEY` | Solo si usa NewsAPI | Clave de NewsAPI para los endpoints de Everything y Top Headlines. |
| `TRANSFORMERS_CACHE` | No | Ruta personalizada donde guardar los modelos descargados. |

> Nota: `lib/db/mongo_client.py` carga automaticamente el `.env`; asegurese de que el archivo existe antes de ejecutar cualquier script.

## Descarga de modelos
Para preparar los modelos de Transformers sin depender de la red en tiempo de ejecucion ejecute:
```bash
python scripts/bootstrap_models.py
```
El script descarga y guarda localmente:
- `distilbert-base-uncased-finetuned-sst-2-english`
- `facebook/bart-large-mnli`
- `facebook/bart-large-cnn`

Si define `TRANSFORMERS_CACHE`, los pesos se guardaran en dicha ruta; de lo contrario se usan los subdirectorios dentro de `models/transformers/`.

## Ejecucion del pipeline principal
1. **Clasificar articulos** (scrapers + NLP):
   ```bash
   python -m ingest.classifier
   ```
   - Crea un identificador de muestra (`sample`) con el formato `uuid4`.
   - Ingiere articulos unicos y almacena los resultados en la coleccion `articles`.
   - Actualiza `link_pool` con `is_articles_processed=True` para cada URL.
   - Registra estadisticas en `metadata` (`topic_distribution`, `sentiment_distribution`, totales procesados y marcas de tiempo).

2. **Explorar datos cargados:**
   ```bash
   python -m outputs.main
   ```
   (Modifique la funcion llamada al final del archivo para listar articulos, metadatos o enlaces segun sea necesario.)

3. **Ingesta via NewsAPI:** utilice `ingest/news_api_scrapper.py` para crear flujos generadores (`scrape_newsapi_stream`, `scrape_all_categories`). Puede integrarlos en el pipeline principal o ejecutarlos manualmente para poblar `link_pool` y `articles`.

## Estructura del repositorio
```
ingest/                # Scrapers, helpers y pipeline de clasificacion
lib/db/                # Conector a MongoDB
lib/repositories/      # Acceso a colecciones MongoDB
models/transformers/   # Cache local de modelos HuggingFace
outputs/               # Scripts de inspeccion y utilidades de consola
scripts/               # Herramientas auxiliares (bootstrap de modelos)
utils/                 # Validaciones compartidas
main.py                # Script de servicio simple (placeholder)
```

## Colecciones de MongoDB
- `link_pool`: control de URLs procesadas; campos `is_articles_processed`, `in_sample` y `sample` evitan duplicados.
- `articles`: articulos clasificados con campos `topic`, `sentiment`, `isCleaned` y metadatos de origen.
- `summaries`: resumenes agrupados por `sample` o `thread_id` para construir narrativas.
- `metadata`: bitacora por lote, con conteos de exito/error y distribuciones calculadas.

Para crear indices recomendados ejecute los metodos `setup_indexes()` definidos en cada repositorio cuando inicialice nuevas instancias.

## Buenas practicas operativas
- Ejecute `scripts/bootstrap_models.py` tras actualizar versiones de Transformers o al desplegar en un entorno nuevo.
- Programe `python -m ingest.classifier` mediante un scheduler (cron, Airflow, etc.) para mantener la base de articulos al dia.
- Supervise el tamaño de `link_pool` para evitar crecimiento indefinido; limpie registros antiguos tras confirmarlos en `articles`.
- Registre excepciones producidas por los scrapers, especialmente cuando los portales cambian su HTML.

## Solucion de problemas
- **Error de conexion a MongoDB:** verifique `MONGO_URI` y la accesibilidad de la base (`lib/db/mongo_client.py`).
- **Descargas de modelos fallidas:** confirme que `TRANSFORMERS_CACHE` apunta a un directorio existente o elimine la variable para usar la ruta por defecto.
- **Articulos duplicados:** revise `LinkPoolRepository.mark_processed` y ejecute `link_pool.setup_indexes()` para imponer unicidad en `url`.
- **Limitaciones de NewsAPI:** cuando se alcancen cuotas, el generador de `scrape_newsapi_stream` registrara el error y detendra la ingesta; configure reintentos externos si es necesario.

## Desarrollo y pruebas
- No existen pruebas automaticas actualmente; se recomienda aislar los cambios en scripts individuales y usar `python -m outputs.main` para validar consultas.
- Para desarrollos de scraping, utilice `ingest/utils.py` para validar la extraccion con `fetch_and_extract` antes de integrar nuevas fuentes.
- Documente nuevos modelos o dependencias agregandolos a `requirements.txt` y actualizando esta guia.
# news-scrawler-ai

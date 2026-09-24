# Catálogo automático INGALITO

Este proyecto toma productos y precios ARS de `https://www.koicelulares.com/`,
calcula el precio de venta de INGALITO y genera un catálogo público listo para
ser consumido por una aplicación web. KOI solo se usa como fuente interna.

## Flujo

1. Scrapy descarga el HTML de KOI y detecta categorías y productos.
2. El spider extrae únicamente el precio publicado en ARS.
3. Playwright se activa solo si una respuesta HTML no contiene productos.
4. `data/koi_raw.json` conserva los datos internos de origen.
5. El procesador compara el RAW anterior, registra altas, bajas, precios y categorías.
6. `data/catalogo.json` contiene exclusivamente los datos públicos de INGALITO.
7. GitHub Actions ejecuta el flujo todos los días a las 09:00 de Argentina.
8. Si hay cambios, hace commit y push para que Vercel pueda reconstruir el sitio.

## Requisitos

- Python 3.14+
- Scrapy 2.19+
- Playwright/Chromium (solo necesario para el respaldo)

En Windows 11:

```powershell
py -3.14 -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python -m playwright install chromium
```

En Linux/macOS:

```bash
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m playwright install chromium
```

## Ejecutar

Scraping solamente:

```bash
scrapy crawl koi -O data/koi_raw.json
```

Actualización completa:

```bash
python -m scripts.actualizar_catalogo
```

Procesar un RAW existente sin red:

```bash
python -m scripts.actualizar_catalogo --skip-scrape
```

El sistema conserva el catálogo anterior si una ejecución válida devuelve menos
de `min_products` productos. Un producto presente con `CONSULTAR` o `CONSULTAR
STOCK` se conserva con `precio_venta: null` y `estado: "consultar"`.

## Configuración

- `config/catalogo.json`: marca pública, WhatsApp de INGALITO y mínimo de seguridad.
- `config/margenes.json`: rangos de costo y margen porcentual.
- `config/precios.json`: múltiplo de redondeo del precio final.

El número de KOI y las URLs de origen no se copian al catálogo público.

## Archivos de salida

- `data/koi_raw.json`: datos internos obtenidos del proveedor.
- `data/catalogo.json`: contrato público para el futuro frontend de INGALITO.
- `data/historial.json`: eventos de productos nuevos, eliminados, precios y categorías.

## Pruebas

```bash
pytest -q
```

Las pruebas cubren extracción ARS frente a USD, productos CONSULTAR, IDs,
márgenes, redondeo, WhatsApp, cambios de precio/categoría, duplicados y la
protección contra scraping vacío.

## GitHub Actions y Vercel

`.github/workflows/actualizar.yml` permite ejecución manual y programa una
ejecución diaria a las 12:00 UTC, equivalente a las 09:00 en Argentina. El job
solo crea un commit si cambió el catálogo, el RAW o el historial. El repositorio
puede conectarse después a Vercel; `data/catalogo.json` es un JSON estático
simple de consumir desde una aplicación web.
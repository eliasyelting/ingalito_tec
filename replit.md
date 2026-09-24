# Catálogo automático INGALITO

Scraper y procesador Python que convierte el catálogo de KOI en un catálogo público de INGALITO.

## Run & Operate

- `pnpm --filter @workspace/api-server run dev` — run the API server (port 5000)
- `pnpm run typecheck` — full typecheck across all packages
- `pnpm run build` — typecheck + build all packages
- `pnpm --filter @workspace/api-spec run codegen` — regenerate API hooks and Zod schemas from the OpenAPI spec
- `pnpm --filter @workspace/db run push` — push DB schema changes (dev only)
- Required env: `DATABASE_URL` — Postgres connection string
- `python -m pip install -r requirements.txt` — instalar dependencias Python
- `python -m scripts.actualizar_catalogo` — ejecutar scraping y procesamiento
- `pytest -q` — ejecutar pruebas del catálogo

## Stack

- pnpm workspaces, Node.js 24, TypeScript 5.9
- API: Express 5
- DB: PostgreSQL + Drizzle ORM
- Validation: Zod (`zod/v4`), `drizzle-zod`
- API codegen: Orval (from OpenAPI spec)
- Build: esbuild (CJS bundle)
- Scraping: Python, Scrapy, scrapy-playwright como respaldo

## Where things live

- `scraper/` — spider Scrapy y extracción de datos RAW
- `catalog/` — IDs, precios, WhatsApp, validación y procesamiento
- `config/` — configuración editable de marca, márgenes y redondeo
- `data/` — RAW interno, catálogo público e historial
- `scripts/actualizar_catalogo.py` — orquestador completo
- `.github/workflows/actualizar.yml` — actualización diaria y push automático

## Architecture decisions

- Scrapy es la ruta normal porque KOI entrega productos y precios ARS en HTML server-rendered.
- Playwright solo se solicita cuando el HTML no contiene ningún producto.
- `data/koi_raw.json` y `data/catalogo.json` están separados para no filtrar costo ni proveedor.
- La actualización aborta si queda por debajo de `min_products`, evitando borrar el catálogo por un fallo del scraper.
- Los precios finales se redondean hacia arriba al múltiplo configurado para no bajar el margen calculado.

## Product

El sistema detecta categorías, altas, bajas, cambios de precio y cambios de categoría, calcula márgenes dinámicos y genera enlaces de WhatsApp con la marca INGALITO.

## User preferences

- La fuente KOI no debe aparecer en el catálogo público.
- Solo deben utilizarse precios publicados en ARS; los precios USD se ignoran.

## Gotchas

_Populate as you build — sharp edges, "always run X before Y" rules._

## Pointers

- See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details

import json
import re
from collections.abc import Iterable


OLD_KOI_WHATSAPP = "5491178953879"


class CatalogValidationError(ValueError):
    """Raised when a catalog cannot be safely published."""


def validate_catalog(
    catalog: dict,
    raw_products: Iterable[dict],
    config: dict,
) -> None:
    products = catalog.get("productos")
    if not isinstance(products, list):
        raise CatalogValidationError("catalogo.json debe tener una lista productos")
    min_products = int(config.get("min_products", 5))
    if len(products) < min_products:
        raise CatalogValidationError(
            f"El catálogo tiene {len(products)} productos; mínimo requerido: {min_products}"
        )

    ids = [product.get("id") for product in products]
    if any(not value for value in ids):
        raise CatalogValidationError("Hay productos sin ID")
    if len(ids) != len(set(ids)):
        raise CatalogValidationError("Hay IDs duplicados")

    source_categories = {item.get("categoria") for item in raw_products}
    required_number = str(config["whatsapp"])
    public_text = json.dumps(catalog, ensure_ascii=False)
    if "KOI" in public_text.upper():
        raise CatalogValidationError("El catálogo público contiene KOI")
    if OLD_KOI_WHATSAPP in public_text:
        raise CatalogValidationError("El catálogo público contiene el WhatsApp de KOI")
    if required_number not in public_text:
        raise CatalogValidationError("El catálogo público no contiene el WhatsApp de INGALITO")

    for product in products:
        name = product.get("nombre")
        category = product.get("categoria")
        state = product.get("estado")
        sale_price = product.get("precio_venta")
        link = product.get("whatsapp_url", "")
        if not isinstance(name, str) or not name.strip():
            raise CatalogValidationError("Hay un producto sin nombre")
        if category not in source_categories:
            raise CatalogValidationError(f"Categoría inválida: {category!r}")
        if state not in {"disponible", "consultar"}:
            raise CatalogValidationError(f"Estado inválido para {name!r}: {state!r}")
        if sale_price is not None and (
            not isinstance(sale_price, int) or isinstance(sale_price, bool) or sale_price <= 0
        ):
            raise CatalogValidationError(f"Precio de venta inválido para {name!r}")
        if state == "consultar" and sale_price is not None:
            raise CatalogValidationError(f"CONSULTAR no puede tener precio: {name!r}")
        if not re.fullmatch(r"https://wa\.me/\d+\?text=.+", link):
            raise CatalogValidationError(f"WhatsApp inválido para {name!r}")

    public_fields = set().union(*(product.keys() for product in products)) if products else set()
    forbidden_fields = {
        "precio_costo",
        "precio_usd",
        "dolar_koi",
        "proveedor",
        "url_origen",
        "url_whatsapp_origen",
    }
    if public_fields & forbidden_fields:
        raise CatalogValidationError(
            f"Campos internos expuestos: {sorted(public_fields & forbidden_fields)}"
        )
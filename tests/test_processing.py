import copy

import pytest

from catalog.processing import build_public_catalog
from catalog.validation import CatalogValidationError


CATALOG_CONFIG = {
    "marca": "INGALITO",
    "whatsapp": "5491124036673",
    "min_products": 5,
}
MARGINS = {
    "0-100000": 25,
    "100001-250000": 22,
    "250001-500000": 18,
    "500001-750000": 15,
    "750001-1000000": 12,
    "1000001-1500000": 10,
    "1500001-2000000": 8,
    "2000001+": 6,
}
PRICES = {"redondeo": 1000}


def raw_products():
    return [
        {
            "id": f"cat__product-{index}",
            "categoria": "CAT",
            "nombre": f"Producto {index}",
            "precio_costo": 100000 + index * 10000,
            "estado": "disponible",
            "url_origen": "https://www.koicelulares.com/",
            "url_whatsapp_origen": "https://wa.me/5491178953879",
        }
        for index in range(1, 6)
    ]


def test_build_catalog_creates_public_fields_and_new_events():
    catalog, events, stats = build_public_catalog(
        raw_products(), [], CATALOG_CONFIG, MARGINS, PRICES
    )
    assert len(catalog["productos"]) == 5
    assert stats["nuevos"] == 5
    assert all("precio_costo" not in product for product in catalog["productos"])
    assert all(
        product["whatsapp"] == "5491124036673"
        and "5491178953879" not in product["whatsapp_url"]
        for product in catalog["productos"]
    )


def test_price_change_is_recorded():
    previous = raw_products()
    current = copy.deepcopy(previous)
    current[0]["precio_costo"] += 50000
    _, events, stats = build_public_catalog(
        current, previous, CATALOG_CONFIG, MARGINS, PRICES
    )
    assert stats["precios_modificados"] == 1
    assert any(event["tipo"] == "precio_aumentado" for event in events)


def test_deleted_product_is_recorded():
    previous = raw_products()
    previous.append(
        {
            **previous[0],
            "id": "cat__product-6",
            "nombre": "Producto 6",
        }
    )
    current = previous[:-1]
    _, events, stats = build_public_catalog(
        current, previous, CATALOG_CONFIG, MARGINS, PRICES
    )
    assert stats["eliminados"] == 1
    assert any(event["tipo"] == "producto_eliminado" for event in events)


def test_consultar_is_kept_without_sale_price():
    current = raw_products()
    current[0]["precio_costo"] = None
    current[0]["estado"] = "consultar"
    catalog, _, stats = build_public_catalog(
        current, [], CATALOG_CONFIG, MARGINS, PRICES
    )
    consultar = next(
        product for product in catalog["productos"] if product["id"] == current[0]["id"]
    )
    assert consultar["estado"] == "consultar"
    assert consultar["precio_venta"] is None
    assert stats["consultar"] == 1


def test_empty_or_small_scrape_is_rejected():
    with pytest.raises(ValueError):
        build_public_catalog([], [], CATALOG_CONFIG, MARGINS, PRICES)
    with pytest.raises(CatalogValidationError):
        build_public_catalog(
            raw_products()[:4], [], CATALOG_CONFIG, MARGINS, PRICES
        )


def test_duplicate_is_rejected():
    current = raw_products() + [raw_products()[0]]
    with pytest.raises(CatalogValidationError):
        build_public_catalog(current, [], CATALOG_CONFIG, MARGINS, PRICES)


def test_margin_configuration_changes_sale_price():
    current = raw_products()
    default_catalog, _, _ = build_public_catalog(
        current, [], CATALOG_CONFIG, MARGINS, PRICES
    )
    higher_margins = dict(MARGINS)
    higher_margins["100001-250000"] = 30
    changed_catalog, _, _ = build_public_catalog(
        current, [], CATALOG_CONFIG, higher_margins, PRICES
    )
    assert changed_catalog["productos"][0]["precio_venta"] >= default_catalog["productos"][0]["precio_venta"]


def test_rounding_configuration_changes_sale_price():
    current = raw_products()
    catalog_1000, _, _ = build_public_catalog(
        current, [], CATALOG_CONFIG, MARGINS, {"redondeo": 1000}
    )
    catalog_100, _, _ = build_public_catalog(
        current, [], CATALOG_CONFIG, MARGINS, {"redondeo": 100}
    )
    first_1000 = catalog_1000["productos"][0]["precio_venta"]
    first_100 = catalog_100["productos"][0]["precio_venta"]
    assert first_1000 % 1000 == 0
    assert first_100 % 100 == 0


def test_whatsapp_configuration_changes_public_links():
    current = raw_products()
    changed_config = {**CATALOG_CONFIG, "whatsapp": "5491100000000"}
    catalog, _, _ = build_public_catalog(
        current, [], changed_config, MARGINS, PRICES
    )
    assert all(product["whatsapp"] == "5491100000000" for product in catalog["productos"])
    assert all("5491100000000" in product["whatsapp_url"] for product in catalog["productos"])


def test_category_change_is_not_reported_as_new_and_deleted():
    previous = raw_products()
    current = copy.deepcopy(previous)
    current[0]["categoria"] = "NUEVA"
    current[0]["id"] = "nueva__producto-1"
    _, events, stats = build_public_catalog(
        current, previous, CATALOG_CONFIG, MARGINS, PRICES
    )
    assert stats["categoria_modificada"] == 1
    assert stats["nuevos"] == 0
    assert stats["eliminados"] == 0
    assert events[0]["tipo"] == "categoria_modificada"
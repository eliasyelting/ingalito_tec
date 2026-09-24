from __future__ import annotations

from datetime import datetime, timezone
from collections import defaultdict
from typing import Any

from catalog.ids import name_key
from catalog.pricing import calculate_price_venta
from catalog.validation import validate_catalog
from catalog.whatsapp import whatsapp_url


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _by_id(products: list[dict]) -> dict[str, dict]:
    return {product["id"]: product for product in products}


def _unique_name_map(products: list[dict]) -> dict[str, dict]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for product in products:
        grouped[name_key(product["nombre"])].append(product)
    return {
        key: values[0]
        for key, values in grouped.items()
        if len(values) == 1
    }


def _event(event_type: str, product: dict, **extra: Any) -> dict:
    payload = {
        "fecha": utc_now(),
        "tipo": event_type,
        "producto": product["nombre"],
        "producto_id": product["id"],
        "categoria": product["categoria"],
    }
    payload.update(extra)
    return payload


def build_public_catalog(
    raw_products: list[dict],
    previous_raw: list[dict],
    catalog_config: dict,
    margins: dict,
    prices_config: dict,
    previous_catalog: dict | None = None,
) -> tuple[dict, list[dict], dict]:
    if not raw_products:
        raise ValueError("El scraper no devolvió productos")

    previous_by_id = _by_id(previous_raw)
    current_by_id = _by_id(raw_products)
    previous_by_name = _unique_name_map(previous_raw)
    current_by_name = _unique_name_map(raw_products)

    category_changes: dict[str, tuple[dict, dict]] = {}
    for key, current in current_by_name.items():
        previous = previous_by_name.get(key)
        if previous and previous["categoria"] != current["categoria"]:
            category_changes[current["id"]] = (previous, current)

    events: list[dict] = []
    category_previous_ids = {previous["id"] for previous, _ in category_changes.values()}
    for current in raw_products:
        previous = previous_by_id.get(current["id"])
        if current["id"] in category_changes:
            old, new = category_changes[current["id"]]
            events.append(
                _event(
                    "categoria_modificada",
                    new,
                    categoria_anterior=old["categoria"],
                    categoria_nueva=new["categoria"],
                )
            )
            previous = old
        elif previous is None:
            events.append(_event("producto_nuevo", current))

        if previous and previous.get("precio_costo") != current.get("precio_costo"):
            old_cost = previous.get("precio_costo")
            new_cost = current.get("precio_costo")
            if old_cost is not None and new_cost is not None:
                event_type = "precio_aumentado" if new_cost > old_cost else "precio_reducido"
                events.append(
                    _event(
                        event_type,
                        current,
                        precio_anterior=old_cost,
                        precio_nuevo=new_cost,
                    )
                )

    for previous in previous_raw:
        if (
            previous["id"] not in current_by_id
            and previous["id"] not in category_previous_ids
        ):
            events.append(_event("producto_eliminado", previous))

    rounding = int(prices_config["redondeo"])
    public_products = []
    margins_applied: dict[str, int] = defaultdict(int)
    for raw in raw_products:
        sale_price, margin = calculate_price_venta(
            raw.get("precio_costo"), margins, rounding
        )
        if margin is not None:
            margins_applied[f"{margin:g}%"] += 1
        public_products.append(
            {
                "id": raw["id"],
                "categoria": raw["categoria"],
                "nombre": raw["nombre"],
                "precio_venta": sale_price,
                "estado": raw["estado"],
                "whatsapp": str(catalog_config["whatsapp"]),
                "whatsapp_url": whatsapp_url(
                    str(catalog_config["whatsapp"]),
                    raw["nombre"],
                    str(catalog_config["marca"]),
                ),
            }
        )

    public_products.sort(key=lambda product: (product["categoria"], product["nombre"]))
    catalog = {"productos": public_products}
    validate_catalog(catalog, raw_products, catalog_config)

    stats = {
        "categorias": len({item["categoria"] for item in raw_products}),
        "productos": len(raw_products),
        "con_precio": sum(item.get("precio_costo") is not None for item in raw_products),
        "consultar": sum(item.get("precio_costo") is None for item in raw_products),
        "margenes_aplicados": dict(margins_applied),
        "nuevos": sum(event["tipo"] == "producto_nuevo" for event in events),
        "eliminados": sum(event["tipo"] == "producto_eliminado" for event in events),
        "precios_modificados": sum(
            event["tipo"] in {"precio_aumentado", "precio_reducido"}
            for event in events
        ),
        "categoria_modificada": sum(
            event["tipo"] == "categoria_modificada" for event in events
        ),
        "playwright": False,
    }
    return catalog, events, stats
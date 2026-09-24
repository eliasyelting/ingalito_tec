import math
import re
from collections.abc import Mapping


def _parse_range(key: str) -> tuple[int, int | None]:
    if key.endswith("+"):
        return int(key[:-1]), None
    lower, upper = key.split("-", 1)
    return int(lower), int(upper)


def margin_for(cost: int, margins: Mapping[str, int | float]) -> float:
    for range_key, margin in margins.items():
        lower, upper = _parse_range(range_key)
        if cost >= lower and (upper is None or cost <= upper):
            return float(margin)
    raise ValueError(f"No hay margen configurado para el costo {cost}")


def calculate_price_venta(
    precio_costo: int | None,
    margins: Mapping[str, int | float],
    rounding: int,
) -> tuple[int | None, float | None]:
    if precio_costo is None:
        return None, None
    if precio_costo < 0:
        raise ValueError("El precio de costo no puede ser negativo")
    if rounding <= 0:
        raise ValueError("El redondeo debe ser mayor que cero")

    margin = margin_for(precio_costo, margins)
    raw_sale_price = precio_costo * (1 + margin / 100)
    sale_price = int(math.ceil(raw_sale_price / rounding) * rounding)
    return sale_price, margin


def parse_ars_price(value: str) -> int:
    if not re.search(r"ARS", value, re.IGNORECASE):
        raise ValueError(f"El valor no contiene ARS: {value!r}")
    digits = re.sub(r"\D", "", value)
    if not digits:
        raise ValueError(f"Precio ARS inválido: {value!r}")
    return int(digits)
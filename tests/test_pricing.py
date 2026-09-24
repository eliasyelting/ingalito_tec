from catalog.pricing import calculate_price_venta, margin_for


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


def test_margin_ranges_include_boundaries():
    assert margin_for(100000, MARGINS) == 25
    assert margin_for(100001, MARGINS) == 22
    assert margin_for(2_000_000, MARGINS) == 8
    assert margin_for(2_000_001, MARGINS) == 6


def test_sale_price_uses_configured_margin_and_rounds_up():
    sale_price, margin = calculate_price_venta(300000, MARGINS, 1000)
    assert sale_price == 354000
    assert margin == 18


def test_consultar_has_no_sale_price():
    assert calculate_price_venta(None, MARGINS, 1000) == (None, None)
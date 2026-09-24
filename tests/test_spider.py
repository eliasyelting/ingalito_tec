from scrapy.http import HtmlResponse, Request

from scraper.spiders.koi import KoiSpider


HTML = """
<html><body>
  <h2>IPHONE</h2>
  <a href="https://wa.me/5491178953879?text=consulta">
    <span class="font-medium leading-tight">iPhone 18 Pro 256GB</span>
    <span>Consultar stock</span>
  </a>
  <a href="https://wa.me/5491178953879?text=venta">
    <span class="font-medium leading-tight">iPhone 17 Pro 256GB</span>
    <span>$1,290 USD</span><span>$2.051.100 ARS</span>
  </a>
  <a href="https://wa.me/5491178953879?text=cta">
    <span class="font-medium leading-tight">¿No encontraste tu equipo? ¡Escribinos!</span>
    <span>CONSULTAR</span>
  </a>
</body></html>
"""


def test_spider_uses_ars_and_ignores_generic_cta():
    spider = KoiSpider()
    response = HtmlResponse(
        url="https://www.koicelulares.com/",
        request=Request("https://www.koicelulares.com/"),
        body=HTML.encode(),
        encoding="utf-8",
    )
    products = list(spider.extract_products(response))
    assert len(products) == 2
    available = next(item for item in products if item["estado"] == "disponible")
    assert available["precio_costo"] == 2051100
    consult = next(item for item in products if item["estado"] == "consultar")
    assert consult["precio_costo"] is None
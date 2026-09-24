import re
import unicodedata
from urllib.parse import urljoin

import scrapy
from scrapy import Request
from scrapy.http import Response
from scrapy_playwright.page import PageMethod

from scraper.items import KoiProductItem


class KoiSpider(scrapy.Spider):
    name = "koi"
    allowed_domains = ["koicelulares.com", "www.koicelulares.com"]
    start_urls = ["https://www.koicelulares.com/"]

    _ars_pattern = re.compile(r"\$\s*([\d.,]+)\s*ARS\b", re.IGNORECASE)
    _consultar_pattern = re.compile(r"\bconsultar(?:\s+stock)?\b", re.IGNORECASE)
    _generic_cta_pattern = re.compile(
        r"no encontraste|escribinos|si buscas alguna|podemos conseguir|contactar por whatsapp",
        re.IGNORECASE,
    )

    def parse(self, response: Response, **kwargs):
        products = list(self.extract_products(response))
        if products or response.meta.get("playwright_fallback"):
            yield from products
            return

        if self.settings.getbool("USE_PLAYWRIGHT_FALLBACK", True):
            self.logger.warning(
                "No se encontraron productos en HTML; reintentando con Playwright"
            )
            yield Request(
                response.url,
                callback=self.parse,
                dont_filter=True,
                meta={
                    "playwright": True,
                    "playwright_fallback": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_load_state", "networkidle"),
                    ],
                },
            )

    def extract_products(self, response: Response):
        seen_ids: set[str] = set()
        links = response.xpath(
            "//a[contains(@href, 'wa.me/') or contains(@href, 'api.whatsapp.com')]"
        )
        for link in links:
            product = self._product_from_link(link, response)
            if product is None or product["id"] in seen_ids:
                continue
            seen_ids.add(product["id"])
            yield product

    def _product_from_link(self, link, response: Response):
        name = self._clean_text(
            link.xpath(
                ".//span[contains(concat(' ', normalize-space(@class), ' '), ' leading-tight ')][1]//text()"
            ).getall()
        )
        if not name or self._generic_cta_pattern.search(name):
            return None

        category = self._clean_text(
            link.xpath("preceding::h2[1]//text()").getall()
        )
        if not category or category.lower() == "el que compra, recomienda.":
            return None

        visible_text = self._clean_text(" ".join(link.xpath(".//text()").getall()))
        cost_match = self._ars_pattern.search(visible_text)
        cost = self.parse_ars_price(cost_match.group(1)) if cost_match else None
        status = "disponible" if cost is not None else "consultar"
        if self._consultar_pattern.search(visible_text):
            status = "consultar"

        source_whatsapp = urljoin(response.url, link.attrib.get("href", ""))
        return KoiProductItem(
            id=self.stable_id(category, name),
            categoria=category,
            nombre=name,
            precio_costo=cost,
            estado=status,
            url_origen=response.url,
            url_whatsapp_origen=source_whatsapp,
        )

    @staticmethod
    def _clean_text(parts) -> str:
        if isinstance(parts, str):
            value = parts
        else:
            value = " ".join(part.strip() for part in parts)
        return re.sub(r"\s+", " ", value).strip()

    @staticmethod
    def parse_ars_price(raw: str) -> int:
        digits = re.sub(r"\D", "", raw)
        if not digits:
            raise ValueError(f"Precio ARS inválido: {raw!r}")
        return int(digits)

    @staticmethod
    def stable_id(category: str, name: str) -> str:
        def slug(value: str) -> str:
            normalized = unicodedata.normalize("NFKD", value)
            ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
            ascii_text = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_text.lower()).strip("-")
            return ascii_text

        return f"{slug(category)}__{slug(name)}"
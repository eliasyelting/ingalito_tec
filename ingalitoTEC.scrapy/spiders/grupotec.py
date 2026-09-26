import scrapy

class GrupotecSpider(scrapy.Spider):
    name = "grupotec"
    allowed_domains = ["grupotecargentina.com"]
    start_urls = ["https://grupotecargentina.com/lista-de-precios/"]

    def parse(self, response):
        # Selecciona los contenedores de los productos
        products = response.css('div.product-card, div.producto, tr.producto-row, .item-producto')

        for prod in products:
            title = prod.css('.title::text, .nombre::text, h3::text, a::text').get()
            if not title:
                continue
            title = title.strip()

            # Evalúa si la etiqueta 'Sin stock' aparece dentro del elemento
            text_block = " ".join(prod.css('*::text').getall())
            in_stock = "Sin stock" not in text_block

            # Extrae únicamente el precio bajo el concepto de 'Transferencia'
            transfer_price = None
            price_nodes = prod.xpath(
                './/*[contains(text(), "Transferencia")]/following-sibling::text() | '
                './/*[contains(text(), "Transferencia")]/parent::*/text()'
            ).getall()

            for text in price_nodes:
                text_clean = text.replace('.', '').replace('$', '').strip()
                if text_clean.isdigit():
                    transfer_price = float(text_clean)
                    break

            if transfer_price:
                yield {
                    'title': title,
                    'price_transfer': transfer_price,
                    'in_stock': in_stock
                }
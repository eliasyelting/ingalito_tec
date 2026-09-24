import scrapy


class KoiProductItem(scrapy.Item):
    id = scrapy.Field()
    categoria = scrapy.Field()
    nombre = scrapy.Field()
    precio_costo = scrapy.Field()
    estado = scrapy.Field()
    url_origen = scrapy.Field()
    url_whatsapp_origen = scrapy.Field()
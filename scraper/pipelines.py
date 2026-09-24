from collections.abc import MutableMapping


class KoiProductPipeline:
    """Keep the feed output limited to the raw fields used by the processor."""

    allowed_fields = (
        "id",
        "categoria",
        "nombre",
        "precio_costo",
        "estado",
        "url_origen",
        "url_whatsapp_origen",
    )

    def process_item(self, item: MutableMapping):
        return {
            key: item[key]
            for key in self.allowed_fields
            if key in item
        }
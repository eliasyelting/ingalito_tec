from urllib.parse import quote


def whatsapp_url(number: str, product_name: str, brand: str) -> str:
    message = f"Hola {brand}, quiero consultar por el {product_name}"
    return f"https://wa.me/{number}?text={quote(message, safe='')}"
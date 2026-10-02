import os
import requests
from bs4 import BeautifulSoup

TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]

PRODUCTS = [
    {
        "store": "Amazon",
        "name": "Producto Amazon 1",
        "url": "https://www.amazon.com.mx/dp/B0HKF2DM2N",
    },
    {
        "store": "Amazon",
        "name": "Producto Amazon 2",
        "url": "https://www.amazon.com.mx/dp/B0HKDZ4LBX",
    },
  
        "store": "Amazon",
        "name": "Producto Amazon 3",
        "url": "https://www.amazon.com.mx/dp/B0HLQZS8DJ",
    },
    {
        "store": "El Palacio de Hierro",
        "name": "Funda Nintendo Switch 2 Zelda 40 aniversario",
        "url": "https://www.elpalaciodehierro.com/nintendo-funda-protectora-para-nintendo-switch-2-edicion-especial-the-legend-of-zelda-40-aniversario-negro-45800825.html",
    },
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) "
        "Version/17.0 Safari/605.1.15"
    )
}


def check_product(product):
    try:
        response = requests.get(
            product["url"],
            headers=HEADERS,
            timeout=20
        )

        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(" ", strip=True).lower()

        if product["store"] == "Amazon":
            unavailable = [
                "actualmente no disponible",
                "no disponible",
                "out of stock",
                "currently unavailable",
            ]

            available = [
                "agregar al carrito",
                "comprar ahora",
                "añadir al carrito",
            ]

        else:
            unavailable = [
                "no disponible",
                "agotado",
            ]

            available = [
                "agregar al carrito",
                "comprar",
            ]

        if any(word in text for word in unavailable):
            status = "AGOTADO"

        elif any(word in text for word in available):
            status = "DISPONIBLE"

        else:
            status = "DESCONOCIDO"

        return status

    except Exception as e:
        return f"ERROR: {e}"


def get_chat_id():
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"

    response = requests.get(url, timeout=20)
    data = response.json()

    updates = data.get("result", [])

    if not updates:
        return None

    return updates[-1]["message"]["chat"]["id"]


def send_message(chat_id, message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    requests.post(
        url,
        data={
            "chat_id": chat_id,
            "text": message,
        },
        timeout=20,
    )


def main():
    print("Iniciando monitor de stock...")

    chat_id = get_chat_id()

    if not chat_id:
        print("No se encontró un chat de Telegram.")
        return

    for product in PRODUCTS:
        status = check_product(product)

        print(
            f"{product['store']} - "
            f"{product['name']} -> {status}"
        )

        if status == "DISPONIBLE":
            message = (
                "🚨 ¡PRODUCTO DISPONIBLE!\n\n"
                f"🏬 {product['store']}\n"
                f"📦 {product['name']}\n\n"
                f"🔗 {product['url']}"
            )

            send_message(chat_id, message)


if __name__ == "__main__":
    main()

import requests
import feedparser

# Token & Chat ID dimasukkan terus secara hardcode
TELEGRAM_TOKEN = "8975926079:AAE1XKNGQTHasdFKr1meRtwT_HDO2gp675s"
TELEGRAM_CHAT_ID = "-1004433036270"

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    res = requests.post(url, json=payload)
    print("Status Hantar Telegram:", res.status_code, res.text)

def check_food_alerts():
    # Hantar mesej ujian pertama terus ke Telegram
    send_telegram_alert("🚨 *UJIAN INTEGRASI RISIKAN IMPORT*\n\nSistem OSINT Food Alert berjaya dihubungkan ke Group Telegram ini.")

    # Semak RSS Feed US FDA
    feed_url = "https://www.fda.gov/about-fda/contact-fda/stay-informed/rss-feeds/food-recalls/rss.xml"
    feed = feedparser.parse(feed_url)
    
    if feed.entries:
        for entry in feed.entries[:2]:
            msg = (
                f"ℹ️ *INFO ALERT IMPOR (US FDA)*\n\n"
                f"*Tajuk:* {entry.title}\n"
                f"*Pautan:* [Buka Laporan]({entry.link})\n\n"
                f"📌 _Tindakan Risikan: Semak rekod pengimportan di FoSIM Import._"
            )
            send_telegram_alert(msg)

if __name__ == "__main__":
    check_food_alerts()

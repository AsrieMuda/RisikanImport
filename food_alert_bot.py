import os
import requests
import feedparser

# Tetapan Telegram (Guna Environment Variables untuk keselamatan)
TELEGRAM_TOKEN = os.getenv("8975926079:AAE1XKNGQTHasdFKr1meRtwT_HDO2gp675s")
TELEGRAM_CHAT_ID = os.getenv("-1004433036270")

# Senarai RSS Feed
FEEDS = {
    "US FDA Food Recalls": "https://www.fda.gov/about-fda/contact-fda/stay-informed/rss-feeds/food-recalls/rss.xml",
}

RISK_KEYWORDS = [
    "aflatoxin", "salmonella", "listeria", "ethylene oxide", 
    "undeclared", "allergen", "unregistered", "prohibited"
]

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    requests.post(url, json=payload)

def check_food_alerts():
    total_alerts_found = 0
    
    for source_name, feed_url in FEEDS.items():
        feed = feedparser.parse(feed_url)
        
        # Ambil 3 entri terkini
        entries = feed.entries[:3] if feed.entries else []
        
        for entry in entries:
            total_alerts_found += 1
            title = entry.title
            link = entry.link
            summary = getattr(entry, 'summary', 'Tiada ringkasan.')

            is_high_risk = any(keyword.lower() in (title + summary).lower() for keyword in RISK_KEYWORDS)
            risk_tag = "🚨 *ALERT BERISIKO TINGGI*" if is_high_risk else "ℹ️ *INFO ALERT IMPOR*"
            
            message = (
                f"{risk_tag}\n\n"
                f"*Sumber:* {source_name}\n"
                f"*Tajuk:* {title}\n\n"
                f"*Pautan:* [Buka Laporan]({link})\n\n"
                f"📌 _Tindakan Risikan: Semak kemasukan berkaitan di FoSIM Import._"
            )
            send_telegram_alert(message)

    # JIKA TIADA DATA BARU / RSS KOSONG, HANTAR STATUS MONITORING
    if total_alerts_found == 0:
        send_telegram_alert("✅ *STATUS RISIKAN:* Imbasan selesai. Tiada amaran makanan (Food Alert) baharu dikesan buat masa ini.")

if __name__ == "__main__":
    check_food_alerts()

import os
import requests
import feedparser

# Tetapan Telegram (Guna Environment Variables untuk keselamatan)
TELEGRAM_TOKEN = os.getenv("8975926079:AAE1XKNGQTHasdFKr1meRtwT_HDO2gp675s")
TELEGRAM_CHAT_ID = os.getenv("-1004433036270")

# Senarai Sumber Feed Alert Antarabangsa
FEEDS = {
    "US FDA Food Recalls": "https://www.fda.gov/about-fda/contact-fda/stay-informed/rss-feeds/food-recalls/rss.xml",
    # Boleh tambah RSS / API lain di sini
}

# Kata kunci berisiko tinggi untuk diberi perhatian khusus
RISK_KEYWORDS = [
    "aflatoxin", "salmonella", "listeria", "ethylene oxide", 
    "undeclared", "allergen", "unregistered", "unauthorized", "prohibited"
]

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)

def check_food_alerts():
    for source_name, feed_url in FEEDS.items():
        feed = feedparser.parse(feed_url)
        
        # Semak 5 tajuk amaran terkini
        for entry in feed.entries[:5]:
            title = entry.title
            link = entry.link
            summary = getattr(entry, 'summary', 'Tiada ringkasan.')

            # Semak jika ada kata kunci berisiko
            is_high_risk = any(keyword.lower() in (title + summary).lower() for keyword in RISK_KEYWORDS)
            
            risk_tag = "🚨 *ALERT BERISIKO TINGGI*" if is_high_risk else "ℹ️ *INFO ALERT MALAM*"
            
            message = (
                f"{risk_tag}\n\n"
                f"*Sumber:* {source_name}\n"
                f"*Tajuk:* {title}\n\n"
                f"*Pautan:* [Klik Sini]({link})\n\n"
                f"📌 _Tindakan Risikan: Semak sebarang pengimportan berkaitan di sistem FoSIM Import._"
            )
            
            # Hantar ke Telegram
            send_telegram_alert(message)

if __name__ == "__main__":
    check_food_alerts()

import os
import requests
import feedparser

TELEGRAM_TOKEN = "8975926079:AAE1XKNGQTHasdFKr1meRtwT_HDO2gp675s"
TELEGRAM_CHAT_ID = "-1004433036270"

FEEDS = {
    "US FDA Food Recalls": "https://www.fda.gov/about-fda/contact-fda/stay-informed/rss-feeds/food-recalls/rss.xml",
    "UK Food Standards Agency": "https://www.food.gov.uk/rss/news-and-alerts/alerts/rss.xml",
    "EU RASFF News": "https://www.foodsafetynews.com/tag/rasff/feed/",
    "Singapore SFA Alerts": "https://www.foodsafetynews.com/tag/singapore-food-agency/feed/"
}

RISK_KEYWORDS = [
    "aflatoxin", "salmonella", "listeria", "ethylene oxide", 
    "undeclared", "allergen", "unregistered", "prohibited", "recall"
]

def send_telegram_alert(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True
        }
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Ralat Telegram: {e}")

def check_food_alerts():
    total_alerts_found = 0
    
    for source_name, feed_url in FEEDS.items():
        try:
            feed = feedparser.parse(feed_url)
            entries = feed.entries[:2] if feed.entries else [] # Ambil 2 entri terkini setiap sumber
            
            for entry in entries:
                total_alerts_found += 1
                title = getattr(entry, 'title', 'Tiada Tajuk')
                link = getattr(entry, 'link', '#')
                summary = getattr(entry, 'summary', '')

                is_high_risk = any(keyword.lower() in (title + summary).lower() for keyword in RISK_KEYWORDS)
                risk_tag = "🚨 *ALERT BERISIKO TINGGI*" if is_high_risk else "ℹ️ *INFO ALERT IMPORT*"
                
                message = (
                    f"{risk_tag}\n\n"
                    f"*Sumber:* {source_name}\n"
                    f"*Tajuk:* {title}\n\n"
                    f"*Pautan:* [Buka Laporan]({link})\n\n"
                    f"📌 _Tindakan Risikan: Semak rekod kemasukan di FoSIM Import._"
                )
                send_telegram_alert(message)
        except Exception as e:
            print(f"Ralat menarik data {source_name}: {e}")

    if total_alerts_found == 0:
        send_telegram_alert("✅ *STATUS RISIKAN:* Imbasan selesai. Tiada amaran baharu dikesan.")

if __name__ == "__main__":
    check_food_alerts()

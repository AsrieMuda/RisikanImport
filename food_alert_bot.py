import os
import requests
import feedparser

TELEGRAM_TOKEN = "8975926079:AAE1XKNGQTHasdFKr1meRtwT_HDO2gp675s"
TELEGRAM_CHAT_ID = "-1004433036270"

FEEDS = {
    "US FDA Food Recalls": "https://www.fda.gov/about-fda/contact-fda/stay-informed/rss-feeds/food-recalls/rss.xml",
    "UK Food Standards Agency": "https://www.food.gov.uk/rss/news-and-alerts/alerts/rss.xml",
    "EU RASFF News": "https://www.foodsafetynews.com/tag/rasff/feed/",
    "Singapore SFA Alerts": "https://www.foodsafetynews.com/tag/singapore-food-agency/feed/",
    "Food Safety News (Global Outbreaks)": "https://www.foodsafetynews.com/feed/"
}

RISK_KEYWORDS = [
    "aflatoxin", "salmonella", "listeria", "ethylene oxide", 
    "undeclared", "allergen", "unregistered", "prohibited", "recall", "outbreak"
]

LOG_FILE = "sent_alerts.txt"

# 1. BACA SENARAI BERITA YANG PERNAH DIHANTAR
def get_sent_alerts():
    if not os.path.exists(LOG_FILE):
        return set()
    with open(LOG_FILE, "r") as f:
        return set(line.strip() for line in f if line.strip())

# 2. SIMPAN PAUTAN BERITA BAHARU
def save_sent_alert(link):
    with open(LOG_FILE, "a") as f:
        f.write(f"{link}\n")

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
    sent_links = get_sent_alerts()
    new_alerts_count = 0
    
    for source_name, feed_url in FEEDS.items():
        try:
            feed = feedparser.parse(feed_url)
            entries = feed.entries[:5] if feed.entries else []
            
            for entry in entries:
                title = getattr(entry, 'title', 'Tiada Tajuk')
                link = getattr(entry, 'link', '#')
                summary = getattr(entry, 'summary', '')

                # JIKA PAUTAN SUDAH PERNAH DIHANTAR, ABAIKAN (SKIP)
                if link in sent_links:
                    continue

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
                save_sent_alert(link)
                sent_links.add(link)
                new_alerts_count += 1
                
        except Exception as e:
            print(f"Ralat menarik data {source_name}: {e}")

    print(f"Selesai imbasan. {new_alerts_count} berita baharu dihantar.")

if __name__ == "__main__":
    check_food_alerts()

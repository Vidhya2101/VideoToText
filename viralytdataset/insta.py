from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
import time
from textblob import TextBlob

#Set up headless browser

options = Options()
options.headless = True
driver = webdriver.Chrome(service=Service('C:\\Users\\Vidhya\\OneDrive\\Desktop\\videototext\\chromedriver.exe'), options=options)

#Input: list of Instagram reel URLs

video_urls = [
"https://www.instagram.com/reel/CtV7Iu1PqD5/",
"https://www.instagram.com/reel/CtZxLo2sdf8/"
]

#Taxonomies (example)

hooks = ["did you know", "stop doing this", "what if I told you"]
ctas = ["follow for more", "like this reel", "drop a comment"]
frameworks = ["listicle", "problem-solution", "storytelling"]

#Data storage

data = []


for url in video_urls:
    driver.get(url)
    time.sleep(5)  # let page load
    try:
        # Views
        views = driver.find_element(By.CSS_SELECTOR, 'span.x1lliihq').text

        # Caption/Transcript
        caption = driver.find_element(By.CSS_SELECTOR, 'h1.x1heor9g span').text

        # Likes + Comments (if visible)
        like_elem = driver.find_elements(By.XPATH, "//span[contains(text(), ' likes')]")
        likes = like_elem[0].text if like_elem else "N/A"

        # Duration (estimated from caption hashtags)
        duration = "0:30" if "#30sec" in caption else "N/A"

        # Hook Detection
        hook_type = next((h for h in hooks if h in caption.lower()), "general")

        # CTA Detection
        cta_type = next((c for c in ctas if c in caption.lower()), "none")

        # Framework Detection
        framework_type = next((f for f in frameworks if f in caption.lower()), "general")

        # Sentiment Score
        sentiment = round(TextBlob(caption).sentiment.polarity, 3)

        # Save data
        data.append({
            "URL": url,
            "Views": views,
            "Caption": caption,
            "Likes": likes,
            "Duration": duration,
            "Hook Type": hook_type,
            "CTA Type": cta_type,
            "Framework Type": framework_type,
            "Sentiment": sentiment
        })
    except Exception as e:
        print(f"Failed on {url} → {e}")



driver.quit()

#Save to Excel

df = pd.DataFrame(data)
df.to_excel("instagram_reel_dataset.xlsx", index=False)
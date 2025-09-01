import requests, time, isodate, os
import pandas as pd
from textblob import TextBlob
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from googleapiclient.discovery import build
from datetime import datetime, timezone
import numpy as np

# API keys for rotation
api_keys = [
    'AIzaSyA2HTWY1JHryGd6U4K-j8_Oz8nVDJHvibw',
    'AIzaSyDoseBtnXGnVf4iz9XqCsZpV07vBO7-FkY',
    'AIzaSyDX9ZMgnaXPfplx1S-bzsafQbyCBaM-WYI'
]
current_key_index = 0

def get_api_key():
    global current_key_index
    key = api_keys[current_key_index]
    current_key_index = (current_key_index + 1) % len(api_keys)
    return key

# Initialize data storage
data = []

# Hook, CTA, Framework taxonomies
hook_types = {
    "targeted_personalised": ["if you're", "for you", "this is for"],
    "personal_experience": ["i did this", "what happened to me"],
    "using_famous_name": ["elon musk", "kylie jenner"],
    "question": ["why does", "how can you", "have you ever"],
    "challenge_or_dare": ["i dare you", "try not to"],
    "statistic_or_fact": ["did you know", "70% of people"],
    "controversial": ["stop doing this", "you're making a mistake"],
    "mystery_or_intrigue": ["you won't believe", "nobody talks about"],
    "tutorial_fix": ["here's how to", "quick fix"],
    "comparison": ["x vs y", "which one is better"],
    "future_prediction": ["in 2030", "what will happen"],
    "negative": ["stop this now", "never do this"]
}

cta_types = {
    "engagement": ["like if you agree", "double tap"],
    "informational": ["follow for more", "save this"],
    "promotion": ["buy now", "check the link"],
    "community": ["tag your friend", "join our group"],
    "feedback": ["comment below", "what do you think"],
    "urgency": ["before it's gone", "last chance"]
}

framework_types = {
    "listicle": ["top 3", "5 things you"],
    "problem_solution": ["struggling with", "here's how"],
    "storytelling": ["my journey", "this happened to me"],
    "before_after_bridge": ["before i did this", "after using this"],
    "question_answer": ["why do we", "here's why"],
    "problem_awareness": ["are you facing", "common mistake"],
    "myth_busting": ["myth or fact", "the truth about"],
    "curiosity_arousal": ["you won't believe", "secret to"],
    "narrative_discovery": ["let's uncover", "discover how"],
    "personal_journey": ["my experience", "i went through"]
}

# Helper functions
def sentiment_score(text):
    return round(TextBlob(text).sentiment.polarity, 3)

def classify_hook(title):
    title_lower = title.lower()
    for key, phrases in hook_types.items():
        if any(phrase in title_lower for phrase in phrases):
            return key
    return "general"

def classify_cta(desc):
    desc_lower = desc.lower()
    for key, phrases in cta_types.items():
        if any(phrase in desc_lower for phrase in phrases):
            return key 
    return "none"

def classify_framework(title):
    title_lower = title.lower()
    for key, phrases in framework_types.items():
        if any(phrase in title_lower for phrase in phrases):
            return key
    return "general"

# YouTube Data API client
def get_youtube_client():
    api_key = get_api_key()
    return build("youtube", "v3", developerKey=api_key)

# Collect data
def fetch_shorts(max_results=5000):
    youtube = get_youtube_client()
    next_page_token = None
    collected = 0

    while collected < max_results:
        request = youtube.search().list(
            part="snippet",
            maxResults=50,
            q="#Shorts",
            type="video",
            videoDuration="short",
            order="viewCount",
            pageToken=next_page_token
        )
        response = request.execute()
        video_ids = [item["id"]["videoId"] for item in response.get("items", [])]

        video_details = youtube.videos().list(
            part="snippet,statistics,contentDetails",
            id=",".join(video_ids)
        ).execute()

        for video in video_details.get("items", []):
            snippet = video["snippet"]
            stats = video["statistics"]
            content = video["contentDetails"]
            vid = video["id"]

            title = snippet.get("title", "")
            desc = snippet.get("description", "")
            views = int(stats.get("viewCount", 0))
            likes = int(stats.get("likeCount", 0))
            comments = int(stats.get("commentCount", 0))
            engagement_rate = round(((likes + comments) / views) * 100, 2) if views else 0
            like_ratio = round((likes / views) * 100, 2) if views else 0
            comment_ratio = round((comments / views) * 100, 2) if views else 0
            published_at = snippet.get("publishedAt")
            upload_date = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
            duration_sec = int(isodate.parse_duration(content["duration"]).total_seconds())
            transcript = "N/A"
            try:
                captions = YouTubeTranscriptApi.get_transcript(vid)
                transcript = " ".join([seg["text"] for seg in captions])
            except (TranscriptsDisabled, NoTranscriptFound, Exception):
                pass

            data.append({
                "Platform": "YouTube",
                "Video ID": vid,
                "Video URL": f"https://www.youtube.com/watch?v={vid}",
                "Title": title,
                "Description": desc,
                "Upload Date": published_at,
                "Views": views,
                "Likes": likes,
                "Comments": comments,
                "Engagement Rate (%)": engagement_rate,
                "Like-to-View Ratio (%)": like_ratio,
                "Comment-to-View Ratio (%)": comment_ratio,
                "Duration (sec)": duration_sec,
                "Transcript": transcript,
                "Hook Type": classify_hook(title),
                "CTA Type": classify_cta(desc),
                "Script Framework Type": classify_framework(title),
                "Title Sentiment": sentiment_score(title)
            })

            collected += 1
            if collected >= max_results:
                break

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

        time.sleep(2)

fetch_shorts(30000)  # 30k videos

# Remove duplicates
df = pd.DataFrame(data)
df.drop_duplicates(subset=["Title", "Description"], inplace=True)
df.to_csv("final_youtube_viral_dataset.csv", index=False)
df.to_excel("final_youtube_viral_dataset.xlsx", index=False)



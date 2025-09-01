import streamlit as st
import yt_dlp
import os
import assemblyai as aai

# Set your AssemblyAI API key
aai.settings.api_key = '30889ab24c6549e9a1ff1530cc801f3d'

# Function to download Instagram reel
def download_instagram_reel(url, output_file='downloaded_video.mp4'):
    ydl_opts = {
        'outtmpl': output_file,
        'format': 'mp4',
        'quiet': True
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return output_file
    except Exception as e:
        return None, str(e)

# Function to transcribe using AssemblyAI
def transcribe_video(file_path):
    try:
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(file_path)
        return transcript.text
    except Exception as e:
        return f"❌ Transcription failed: {str(e)}"

# Streamlit UI
st.set_page_config(page_title="Instagram Reel to Transcript", layout="centered")
st.title("📹 Instagram Reel to Transcript 📝")

url = st.text_input("Paste the Instagram Reel URL here:")

if st.button("Get Transcript"):
    if url:
        with st.spinner("🔄 Downloading reel..."):
            video_path = download_instagram_reel(url)
        
        if not video_path or not os.path.exists(video_path):
            st.error("❌ Failed to download the Instagram video.")
        else:
            with st.spinner("🧠 Transcribing..."):
                result = transcribe_video(video_path)

            st.success("✅ Transcript ready!")

            st.subheader("📝 Transcript:")
            st.markdown(
    f"<div style='background-color:#f7f7f7;color:#111;padding:15px;border-radius:10px;height:300px;overflow:auto;white-space:pre-wrap'>{result}</div>",
    unsafe_allow_html=True
)


            # Clean up file
            os.remove(video_path)
    else:
        st.warning("⚠️ Please enter a valid Instagram reel URL.")

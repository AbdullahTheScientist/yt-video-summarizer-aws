# import os
# import re
# from flask import Flask, request, jsonify
# import google.generativeai as genai
# from dotenv import load_dotenv
# from youtube_transcript_api import YouTubeTranscriptApi
# import requests
# from tenacity import retry, stop_after_attempt, wait_exponential

# # Load environment variables
# load_dotenv()
# genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# app = Flask(__name__)

# def extract_video_id(youtube_url):
#     """Extracts video ID from various YouTube URL formats."""
#     patterns = [
#         r'(?:v=|\/)([0-9A-Za-z_-]{11})',  # Matches v=VIDEOID or /VIDEOID
#         r'youtu.be\/([0-9A-Za-z_-]{11})'  # Matches youtu.be/VIDEOID
#     ]
#     for pattern in patterns:
#         match = re.search(pattern, youtube_url)
#         if match:
#             return match.group(1)
#     return None

# @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
# def fetch_transcript_with_retry(video_id):
#     """Fetches transcript with retries and custom headers."""
#     session = requests.Session()
#     session.headers.update({
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
#         'Accept-Language': 'en-US,en;q=0.9',
#     })
#     return YouTubeTranscriptApi.get_transcript(video_id, session=session)

# def extract_transcript(youtube_video_url):
#     """Extracts transcript from a given YouTube URL."""
#     try:
#         video_id = extract_video_id(youtube_video_url)
#         if not video_id:
#             return "Error: Invalid YouTube URL"
        
#         transcript_text = fetch_transcript_with_retry(video_id)
#         transcript = " ".join([i["text"] for i in transcript_text])
#         return transcript
#     except Exception as e:
#         return f"Error: {str(e)}"

# def generate_summary(transcript_text, words):
#     """Generates a summary based on the transcript and word limit."""
#     prompt = f"""
#     Summarize the following transcript into {words} words, highlighting key points:
#     {transcript_text}
#     """
#     model = genai.GenerativeModel("gemini-pro")
#     response = model.generate_content(prompt)
#     return response.text if response else "Error generating summary."

# @app.route('/')
# def index():
#     return {
#         "message": "Hello Mr. Hanif! Here are the available routes:",
#         "routes": {
#             "/transcript": "Get the transcription of a YouTube video",
#             "/summarize": "Summarize the transcribed text",
#             "/ask": "Chatbot interaction"
#         },
#         "parameters": {
#             "/transcript": ["youtube_link"],
#             "/summarize": ["youtube_link", "words"],
#             "/ask": ["summary", "user_input"]
#         }
#     }

# @app.route('/transcript', methods=['POST'])
# def get_transcript():
#     """API endpoint to fetch YouTube video transcript."""
#     data = request.get_json()
#     youtube_link = data.get("youtube_link")
    
#     if not youtube_link:
#         return jsonify({"error": "YouTube video link is required"}), 400
    
#     transcript = extract_transcript(youtube_link)
#     if transcript.startswith("Error"):
#         return jsonify({"error": transcript}), 500
    
#     return jsonify({"transcript": transcript}), 200

# @app.route('/summarize', methods=['POST'])
# def summarize_video():
#     """API endpoint to summarize a YouTube video."""
#     data = request.get_json()
#     youtube_link = data.get("youtube_link")
#     word_count = data.get("word_count", 100)  # Default to 100 words
    
#     if not youtube_link:
#         return jsonify({"error": "YouTube video link is required"}), 400
    
#     transcript_text = extract_transcript(youtube_link)
#     if transcript_text.startswith("Error"):
#         return jsonify({"error": transcript_text}), 500
    
#     summary = generate_summary(transcript_text, word_count)
#     return jsonify({"summary": summary}), 200

# @app.route('/ask', methods=['POST'])
# def ask_question():
#     """API endpoint to ask a question about the summary."""
#     data = request.get_json()
#     user_input = data.get("user_input")
#     summary = data.get("summary")
    
#     if not user_input or not summary:
#         return jsonify({"error": "Both user input and summary are required"}), 400
    
#     response = genai.GenerativeModel("gemini-pro").generate_content(
#         f"""
#             You are an intelligent assistant. Provide a well-structured and informative response based on the Summary below.
#             - If the user's question is directly related to the Summary, answer it accurately.
#             - If the question is somewhat related but not explicitly covered in the Summary, provide relevant insights or background information.
#             - If the question is unrelated, politely redirect the user toward discussing the Summary content.

#         {summary}
        
#         User: {user_input}
#         """
#     )
    
#     return jsonify({"response": response.text if response else "Error generating response."}), 200

# if __name__ == '__main__':
#     app.run(host="0.0.0.0", debug=True)  # Change port to 5001 or any other available port








import os
import re
from flask import Flask, request, jsonify
import google.generativeai as genai
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

app = Flask(__name__)

SEARCHAPI_KEY = "Z2wqZhz9cnuXNLXWBKtDHmjA"

def extract_video_id(youtube_url):
    """Extracts video ID from various YouTube URL formats."""
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11})',  # Matches v=VIDEOID or /VIDEOID
        r'youtu.be\/([0-9A-Za-z_-]{11})'  # Matches youtu.be/VIDEOID
    ]
    for pattern in patterns:
        match = re.search(pattern, youtube_url)
        if match:
            return match.group(1)
    return None

def fetch_transcript(video_id):
    """Fetches transcript using SearchAPI."""
    url = "https://www.searchapi.io/api/v1/search"
    params = {
        "engine": "youtube_transcripts",
        "video_id": video_id,
        "api_key": SEARCHAPI_KEY
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        transcripts = data.get("transcripts", [])
        transcript_text = " ".join([t["text"] for t in transcripts])
        return transcript_text if transcript_text else "Error: No transcript available."
    else:
        return f"Error: {response.status_code}, {response.text}"

def generate_summary(transcript_text, words):
    """Generates a summary based on the transcript and word limit."""
    prompt = f"""
    Summarize the following transcript into {words} words, highlighting key points:
    {transcript_text}
    """
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    return response.text if response else "Error generating summary."

@app.route('/transcript', methods=['POST'])
def get_transcript():
    """API endpoint to fetch YouTube video transcript."""
    data = request.get_json()
    youtube_link = data.get("youtube_link")
    
    if not youtube_link:
        return jsonify({"error": "YouTube video link is required"}), 400
    
    video_id = extract_video_id(youtube_link)
    if not video_id:
        return jsonify({"error": "Invalid YouTube URL"}), 400
    
    transcript = fetch_transcript(video_id)
    if transcript.startswith("Error"):
        return jsonify({"error": transcript}), 500
    
    return jsonify({"transcript": transcript}), 200

@app.route('/summarize', methods=['POST'])
def summarize_video():
    """API endpoint to summarize a YouTube video."""
    data = request.get_json()
    youtube_link = data.get("youtube_link")
    word_count = data.get("word_count", 100)  # Default to 100 words
    
    if not youtube_link:
        return jsonify({"error": "YouTube video link is required"}), 400
    
    video_id = extract_video_id(youtube_link)
    if not video_id:
        return jsonify({"error": "Invalid YouTube URL"}), 400
    
    transcript_text = fetch_transcript(video_id)
    if transcript_text.startswith("Error"):
        return jsonify({"error": transcript_text}), 500
    
    summary = generate_summary(transcript_text, word_count)
    return jsonify({"summary": summary}), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)

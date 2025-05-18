import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from youtube_transcript_api import YouTubeTranscriptApi
from transformers import pipeline
from urllib.parse import urlparse, parse_qs

from django.shortcuts import render

def home(request):
    return render(request, "index.html")

@csrf_exempt
def summarize_video(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            video_url = data.get("url", "")
            video_id = extract_video_id(video_url)

            if not video_id:
                return JsonResponse({"error": "Invalid YouTube URL"}, status=400)

            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            full_text = " ".join([entry['text'] for entry in transcript])

            summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
            summary = summarizer(full_text[:1024])[0]['summary_text']

            return JsonResponse({"summary": summary})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)

def extract_video_id(url):
    try:
        query = urlparse(url)
        if query.hostname in ["www.youtube.com", "youtube.com"]:
            return parse_qs(query.query).get("v", [None])[0]
        elif query.hostname == "youtu.be":
            return query.path[1:]
    except:
        return None

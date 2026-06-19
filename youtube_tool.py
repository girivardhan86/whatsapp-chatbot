# youtube_tool.py

from youtube_transcript_api import YouTubeTranscriptApi
from langchain_core.documents import Document
from create_vector_db import _store_docs

def ingest_youtube(url, user_id):

    try:

        # extract video id
        video_id = url.split("v=")[1].split("&")[0]

        # get transcript
        transcript = YouTubeTranscriptApi.get_transcript(video_id)

        text = " ".join([
            item["text"]
            for item in transcript
        ])

        docs = [
            Document(
                page_content=text,
                metadata={
                    "source": url,
                    "type": "youtube"
                }
            )
        ]

        _store_docs(docs, user_id)

        return "✅ YouTube video processed successfully."

    except Exception as e:

        print("YouTube Error:", e)

        return "❌ Failed to process YouTube video."
from googleapiclient.discovery import build
from dotenv import load_dotenv
import os
import csv

# Load API key from .env
load_dotenv()
API_KEY = os.getenv('YOUTUBE_API_KEY')
CHANNEL_ID = 'UC_x5XG1OV2P6uZZ5FSM9Ttw'  

youtube = build('youtube', 'v3', developerKey=API_KEY)

def get_uploads_playlist_id(channel_id):
    res = youtube.channels().list(
        part='contentDetails',
        id=channel_id
    ).execute()
    return res['items'][0]['contentDetails']['relatedPlaylists']['uploads']

def get_video_ids(playlist_id):
    video_ids = []
    next_page_token = None
    while True:
        res = youtube.playlistItems().list(
            part='contentDetails',
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        ).execute()
        for item in res['items']:
            video_ids.append(item['contentDetails']['videoId'])

        next_page_token = res.get('nextPageToken')
        if not next_page_token:
            break
    return video_ids

def get_video_details(video_ids):
    all_details = []
    for i in range(0, len(video_ids), 50):  
        response = youtube.videos().list(
            part='snippet,contentDetails,statistics',
            id=','.join(video_ids[i:i+50])
        ).execute()

        for video in response['items']:
            info = {
                'title': video['snippet']['title'],
                'videoId': video['id'],
                'description': video['snippet'].get('description', ''),
                'publishedAt': video['snippet']['publishedAt'],
                'channelTitle': video['snippet']['channelTitle'],
                'tags': ','.join(video['snippet'].get('tags', [])),
                'categoryId': video['snippet']['categoryId'],
                'duration': video['contentDetails']['duration'],
                'viewCount': video['statistics'].get('viewCount'),
                'likeCount': video['statistics'].get('likeCount'),
                'commentCount': video['statistics'].get('commentCount')
            }
            all_details.append(info)
    return all_details

def save_to_csv(data, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

if __name__ == "__main__":
    playlist_id = get_uploads_playlist_id(CHANNEL_ID)
    video_ids = get_video_ids(playlist_id)
    video_metadata = get_video_details(video_ids)

    save_path = 'data/raw/youtube_video_metadata.csv'
    save_to_csv(video_metadata, save_path)
    print(f"✅ Video metadata saved to: {save_path}")

    print("✅ ETL pipeline completed.")
import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text
from googleapiclient.discovery import build
from dotenv import load_dotenv

# ─── CONFIG & CONNECTION ───────────────────────────────────────────────────────
load_dotenv()

SQL_USER   = os.getenv("SQLSERVER_USER", "")
SQL_PWD    = os.getenv("SQLSERVER_PASSWORD", "")
SQL_HOST   = os.getenv("SQLSERVER_HOST", "localhost\\SQLEXPRESS")
SQL_DB     = os.getenv("SQLSERVER_DB", "youtube_data")
SQL_DRIVER = os.getenv("SQLSERVER_DRIVER", "ODBC Driver 17 for SQL Server")

driver_enc = SQL_DRIVER.replace(" ", "+")
if SQL_USER and SQL_PWD:
    # SQL Authentication
    conn_str = (
        f"mssql+pyodbc://{SQL_USER}:{SQL_PWD}@{SQL_HOST}/{SQL_DB}"
        f"?driver={driver_enc}"
    )
else:
    # Windows Authentication
    conn_str = (
        f"mssql+pyodbc://@{SQL_HOST}/{SQL_DB}"
        f"?driver={driver_enc}&trusted_connection=yes"
    )

engine  = create_engine(conn_str, fast_executemany=True)
youtube = build("youtube", "v3", developerKey=os.getenv("YOUTUBE_API_KEY"))

#PATH HELPERS 
# project root is one level up from this file
BASE_DIR      = Path(__file__).resolve().parent.parent
RAW_VIDEO_CSV = BASE_DIR / "data" / "raw" / "youtube_video_metadata.csv"

# DIMENSION: CHANNEL 
def load_dim_channel(channel_id: str):
    info = (
        youtube.channels()
        .list(part="snippet,statistics", id=channel_id)
        .execute()["items"][0]
    )
    row = {
        "channel_id"   : info["id"],
        "channel_name" : info["snippet"]["title"],
        "subscribers"  : int(info["statistics"].get("subscriberCount", 0)),
        "total_videos" : int(info["statistics"].get("videoCount",    0)),
    }
    df = pd.DataFrame([row])

    merge_sql = """
    MERGE dim_channel AS target
    USING stg_dim_channel AS src
      ON target.channel_id = src.channel_id
    WHEN MATCHED THEN
      UPDATE SET
        channel_name = src.channel_name,
        subscribers  = src.subscribers,
        total_videos = src.total_videos
    WHEN NOT MATCHED THEN
      INSERT (channel_id, channel_name, subscribers, total_videos)
      VALUES (src.channel_id, src.channel_name, src.subscribers, src.total_videos);
    """

    with engine.begin() as conn:
        df.to_sql("stg_dim_channel", conn, if_exists="replace", index=False)
        conn.execute(text(merge_sql))
        conn.execute(text("DROP TABLE stg_dim_channel;"))

    print(" dim_channel merged")

#  FACT: VIDEO 
def load_fact_video(csv_path: Path = RAW_VIDEO_CSV):
    # <- csv_path is a pathlib.Path, built above, so no \-escapes!
    raw = pd.read_csv(csv_path)

    raw["upload_date"] = pd.to_datetime(raw["publishedAt"]).dt.date
    raw["views"]       = pd.to_numeric(raw["viewCount"],    errors="coerce")
    raw["likes"]       = pd.to_numeric(raw["likeCount"],    errors="coerce")
    raw["comments"]    = pd.to_numeric(raw["commentCount"], errors="coerce")
    raw["channel_id"]  = raw.get("channel_id", "UC_x5XG1OV2P6uZZ5FSM9Ttw")

    fact = (
        raw[[
          "videoId","channel_id","title","views","likes","comments",
          "upload_date","duration","tags","categoryId","description"
        ]]
        .rename(columns={"videoId":"video_id","categoryId":"category_id"})
    )

    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS fact_video;"))
        fact.to_sql("fact_video", conn, if_exists="replace", index=False)

    print(" fact_video loaded")

#ENTRY POINT 
if __name__ == "__main__":
    CHANNEL_ID = "UC_x5XG1OV2P6uZZ5FSM9Ttw"
    load_dim_channel(CHANNEL_ID)
    load_fact_video()

import os
import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus
from dotenv import load_dotenv
from pathlib import Path

#  LOAD ENV 
load_dotenv()

# SQL SERVER CONNECTION SETUP 
SQL_HOST   = os.getenv("SQLSERVER_HOST", "MANI\\SQLEXPRESS")
SQL_DB     = os.getenv("SQLSERVER_DB",     "youtube_data")
SQL_DRIVER = os.getenv("SQLSERVER_DRIVER", "ODBC Driver 17 for SQL Server")

# Build an ODBC connection string that uses Windows Authentication
odbc_str = (
    f"DRIVER={{{SQL_DRIVER}}};"
    f"SERVER={SQL_HOST};"
    f"DATABASE={SQL_DB};"
    "Trusted_Connection=yes;"
)

# URL-encode it for SQLAlchemy
conn_url = "mssql+pyodbc:///?odbc_connect=" + quote_plus(odbc_str)
engine   = create_engine(conn_url, fast_executemany=True)

#LOAD & TRANSFORM 
# Define the path to your CSV reliably, regardless of CWD:
BASE_DIR   = Path(__file__).resolve().parent.parent
CSV_PATH   = BASE_DIR / "data" / "raw" / "youtube_video_metadata.csv"

# 1) Read
df = pd.read_csv(CSV_PATH)

# 2) Transform columns
df["upload_date"] = pd.to_datetime(df["publishedAt"]).dt.date
df["views"]       = pd.to_numeric( df["viewCount"],    errors="coerce" )
df["likes"]       = pd.to_numeric( df["likeCount"],    errors="coerce" )
df["comments"]    = pd.to_numeric( df["commentCount"], errors="coerce" )
df["channel_id"]  = "UC_x5XG1OV2P6uZZ5FSM9Ttw"

fact_video = (
    df[[
      "videoId","channel_id","title","views","likes","comments",
      "upload_date","duration","tags","categoryId","description"
    ]]
    .rename(columns={
      "videoId":     "video_id",
      "categoryId":  "category_id"
    })
)

#WRITE TO SQL SERVER 
fact_video.to_sql(
    "fact_video",
    con=engine,
    if_exists="replace",
    index=False
)

print("Data loaded into SQL Server with Windows Authentication!")

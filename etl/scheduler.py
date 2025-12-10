import schedule
import time
import subprocess

def job():
    print("⏳ Fetching real-time data from YouTube...")
    subprocess.run(["python", "etl/extract.py"])
    subprocess.run(["python", "etl/checking.py"])
    subprocess.run(["python", "etl/load.py"])
    print("✅ ETL pipeline completed.\n")

#  Choose one of these schedule lines:

# Option 1: Run every hour
#schedule.every(1).hours.do(job)

# Option 2: Run every 10 minutes
# schedule.every(10).minutes.do(job)

# Option 3: Run daily at 2 AM
#schedule.every().day.at("02:00").do(job)

# Initial call to run immediately
print("🕒 Scheduler started.")
job()

while True:
    schedule.run_pending()
    time.sleep(1)

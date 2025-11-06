# Tubelytics Backend (Django)

This is the Django backend for Tubelytics.  
It exposes APIs to resolve YouTube channel URLs/IDs, fetch channel + video data using the YouTube Data API, and serve that data to the frontend.

---

## 1. Setup

```bash
cd backend

# (optional but recommended)
python -m venv venv
# Windows:
venv\Scripts\activate

pip install -r requirements.txt

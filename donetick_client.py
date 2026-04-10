import requests
from datetime import datetime
import os

# Default configuration from environment variables
DONETICK_BASE_URL = os.getenv("DONETICK_BASE_URL", "https://donetick.com")
DONETICK_SECRET_KEY = os.getenv("DONETICK_SECRET_KEY")

def get_chores_due_today(base_url=DONETICK_BASE_URL, secret_key=DONETICK_SECRET_KEY):
    """
    Queries the Donetick API for chores and filters those due today.
    """
    if not secret_key:
        raise ValueError("DONETICK_SECRET_KEY is required")

    url = f"{base_url.rstrip('/')}/eapi/v1/chore"
    headers = {
        "secretkey": secret_key,
        "Accept": "application/json"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    all_chores = response.json()
    today_str = datetime.now().strftime("%Y-%m-%d")
    print(today_str)
    print(all_chores)
    
    # Filter chores where next_due_date starts with today's date (YYYY-MM-DD)
    chores_due_today = [
        chore for chore in all_chores 
        if chore.get("nextDueDate") and chore["nextDueDate"].startswith(today_str)
    ]
    
    return chores_due_today

def mark_chore_complete(chore_id, base_url=DONETICK_BASE_URL, secret_key=DONETICK_SECRET_KEY):
    """
    Marks a given chore as complete by its ID.
    Note: This endpoint is restricted to Donetick Plus members.
    """
    if not secret_key:
        raise ValueError("DONETICK_SECRET_KEY is required")

    url = f"{base_url.rstrip('/')}/eapi/v1/chore/{chore_id}/complete"
    headers = {
        "secretkey": secret_key,
        "Accept": "application/json"
    }
    
    response = requests.post(url, headers=headers)
    response.raise_for_status()
    
    return response.json()

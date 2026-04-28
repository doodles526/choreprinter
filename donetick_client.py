import requests
from datetime import datetime
import os

# Default configuration from environment variables
DONETICK_BASE_URL = os.getenv("DONETICK_BASE_URL", "https://donetick.com")
DONETICK_SECRET_KEY = os.getenv("DONETICK_SECRET_KEY")

def get_all_due_chores(base_url=DONETICK_BASE_URL, secret_key=DONETICK_SECRET_KEY):
    """
    Queries the Donetick API for chores and filters those due today or earlier.
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
    today = datetime.now().date()
    
    due_chores = []
    for chore in all_chores:
        next_due_str = chore.get("nextDueDate")
        if next_due_str:
            try:
                dt_utc = datetime.fromisoformat(next_due_str.replace('Z', '+00:00'))
                dt_local = dt_utc.astimezone()
                
                # Check if due today or in the past
                if dt_local.date() <= today:
                    due_chores.append(chore)
            except ValueError:
                if next_due_str[:10] <= today.strftime("%Y-%m-%d"):
                    due_chores.append(chore)
    
    return due_chores

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
    today = datetime.now().date()
    
    chores_due_today = []
    for chore in all_chores:
        next_due_str = chore.get("nextDueDate")
        if next_due_str:
            try:
                # Handle 'Z' by replacing it with '+00:00' to support older Python fromisoformat
                dt_utc = datetime.fromisoformat(next_due_str.replace('Z', '+00:00'))
                # Convert to local timezone
                dt_local = dt_utc.astimezone()
                
                if dt_local.date() == today:
                    chores_due_today.append(chore)
            except ValueError:
                # Fallback to simple string check if parsing fails
                if next_due_str.startswith(today.strftime("%Y-%m-%d")):
                    chores_due_today.append(chore)
    
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

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time

def get_events_for_month(month, year):
    url = f"https://www.whatcomcounty.us/calendar.aspx?CID=55&month={month}&year={year}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'lxml')
    events_data = []
    
    # Find all event containers
    event_elements = soup.find_all('div', {'itemscope': True, 'itemtype': 'http://schema.org/Event'})
    
    for event in event_elements:
        name_tag = event.find('span', {'itemprop': 'name'})
        if name_tag and "Punch Card" in name_tag.text:
            start_date_tag = event.find('span', {'itemprop': 'startDate'})
            
            if start_date_tag:
                dt_str = start_date_tag.text.strip()
                try:
                    # ISO format: 2026-04-08T05:40:00
                    dt = datetime.fromisoformat(dt_str)
                    
                    # Try to get readable date from subHeader
                    readable_date = None
                    parent_hidden = event.find_parent('div', class_='hidden')
                    if parent_hidden:
                        sub_header = parent_hidden.find('div', class_='subHeader')
                        if sub_header:
                            date_div = sub_header.find('div', class_='date')
                            if date_div:
                                readable_date = date_div.text.strip().replace('\xa0', ' ')
                    
                    events_data.append({
                        "name": name_tag.text.strip(),
                        "datetime": dt,
                        "readable_date": readable_date or dt.strftime("%B %d, %Y, %I:%M %p")
                    })
                except ValueError:
                    continue
                    
    # Sort events by date
    events_data.sort(key=lambda x: x["datetime"])
    return events_data

def find_next_punch_card_event():
    now = datetime.now()
    current_month = now.month
    current_year = now.year
    
    # Search up to 6 months ahead
    for i in range(6):
        month = (current_month + i - 1) % 12 + 1
        year = current_year + (current_month + i - 1) // 12
        
        print(f"Checking {datetime(year, month, 1).strftime('%B %Y')}...")
        
        try:
            month_events = get_events_for_month(month, year)
            
            # Find the first event that is in the future
            for event in month_events:
                if event["datetime"] >= now:
                    print("\nNext Punch Card Event Found:")
                    print(f"Event: {event['name']}")
                    print(f"Date:  {event['readable_date']}")
                    return event
                    
        except Exception as e:
            print(f"Error checking {month}/{year}: {e}")
            
        # Small delay to be polite to the server
        time.sleep(0.5)
        
    print("\nNo upcoming Punch Card events found in the next 6 months.")
    return None

if __name__ == "__main__":
    find_next_punch_card_event()

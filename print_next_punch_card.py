import parse_calendar
import printer
import sys
from datetime import datetime

def main():
    try:
        print("Searching for the next Ferry Punch Card event...")
        next_event = parse_calendar.find_next_punch_card_event()
        
        if not next_event:
            print("No upcoming events found.")
            return

        # Calculate days remaining
        now = datetime.now()
        days_left = (next_event['datetime'].date() - now.date()).days
        
        if days_left > 5:
            print(f"\nNext event '{next_event['name']}' is {days_left} days away.")
            print("Skipping print (event is more than 5 days out).")
            return

        print(f"\nPreparing to print: {next_event['name']} on {next_event['readable_date']} ({days_left} days away)")
        
        # Create the image from the event data
        event_img = printer.create_event_image(next_event)
        
        # Send to printer
        print("Sending to printer...")
        printer.print_image(event_img)
        print("Print successful!")
        
    except Exception as e:
        print(f"Error during printing process: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

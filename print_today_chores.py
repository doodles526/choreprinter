import donetick_client
import printer
from datetime import datetime

def transform_chore_to_todo(chore):
    """
    Transforms a Donetick chore dictionary into the 'todo' structure 
    required by printer.py.
    """
    # Mapping Donetick fields to the printer's todo structure
    # 'name' -> 'title'
    # 'description' -> 'note'
    # 'assigned_to' -> 'assigned_to' (Donetick gives an ID, we'll use a placeholder or ID)
    # 'next_due_date' -> 'finish_by'
    
    return {
        "title": chore.get("name", "Untitled Chore"),
        "note": chore.get("description", ""),
        "assigned_to": str(chore.get("assigned_to") or "Someone"),
        "date_assigned": datetime.now().strftime("%Y-%m-%d"),
        "finish_by": chore.get("next_due_date", "Today")
    }

def main():
    try:
        print("Fetching chores due today...")
        today_chores = donetick_client.get_chores_due_today()
        
        if not today_chores:
            print("No chores due today.")
            return

        print(f"Found {len(today_chores)} chores. Printing...")
        
        for chore in today_chores:
            todo = transform_chore_to_todo(chore)
            print(f"Printing: {todo['title']}")
            printer.image_from_todo(todo)
            
            # Mark the chore as complete in Donetick after successful print
            print(f"Marking chore {chore['id']} as complete...")
            donetick_client.mark_chore_complete(chore['id'])
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

import json
import os
import shutil
from datetime import datetime

def process_term_bank(file_path):
    """
    Processes a JSON file to format definitions and handle example sentences.
    """
    data = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: The file '{file_path}' is not a valid JSON file.")
        return
        
    def update_content(obj):
        """
        Recursively finds and updates content based on user requests.
        """
        if isinstance(obj, dict):
            # Update styles
            if 'style' in obj and isinstance(obj['style'], dict):
                style = obj['style']
                if style.get('fontSize') == '0.9em':
                    style['fontSize'] = '1em'
                if style.get('color') == '#444':
                    style['color'] = '#a8a8a8'

            # Replace newlines
            if 'content' in obj and isinstance(obj['content'], str):
                obj['content'] = obj['content'].replace('\\n', '\n')
            
            # Recursively process content
            for key, value in obj.items():
                update_content(value)
        
        elif isinstance(obj, list):
            new_list = []
            for item in obj:
                # Remove unwanted tags
                if isinstance(item, dict):
                    if item.get('tag') == 'div' and item.get('style') and item['style'].get('fontStyle') == 'italic' and item.get('content') == 'Noun':
                        continue
                    if item.get('tag') == 'details' and item.get('content') and item['content'][0].get('content') == 'Example Sentences':
                        continue
                
                # Recursively process remaining items
                update_content(item)
                new_list.append(item)
            obj[:] = new_list

    # Apply all updates
    update_content(data)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\nSuccessfully processed and updated '{file_path}'.")
    print(f"Total terms: {len(data)}")

if __name__ == "__main__":
    INPUT_FILE = "term_bank_1.json"
    BACKUP_DIR = "backups"

    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
        print(f"Created directory: {BACKUP_DIR}")

    if os.path.exists(INPUT_FILE):
        timestamp = datetime.now().strftime("%m_%d_%y")
        backup_path = os.path.join(BACKUP_DIR, f"term_bank_1_BACKUP_{timestamp}.json")
        try:
            shutil.copy2(INPUT_FILE, backup_path)
            print(f"Created backup of '{INPUT_FILE}' at '{backup_path}'")
        except Exception as e:
            print(f"Error creating backup: {e}")

        process_term_bank(INPUT_FILE)
    else:
        print(f"Error: The file '{INPUT_FILE}' does not exist.")

    # Added to prevent the console from closing immediately
    input("Press Enter to exit...")
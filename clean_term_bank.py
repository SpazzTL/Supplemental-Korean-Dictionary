import json
import os
import shutil
from datetime import datetime

def is_example_sentence_with_content(item):
    """
    Checks if a 'details' tag has the 'Example Sentences' summary
    and contains a non-empty list of examples.
    """
    if item.get('tag') != 'details':
        return False
    
    if not item.get('content') or item['content'][0].get('content') != 'Example Sentences':
        return False
        
    if len(item.get('content', [])) < 2:
        return False
    
    ul_tag = item['content'][1]
    
    if ul_tag.get('tag') == 'ul':
        for li_item in ul_tag.get('content', []):
            if li_item.get('content'):
                return True
                
    return False

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

    for entry in data:
        if isinstance(entry[0], str):
            entry[0] = entry[0].strip()
            
        structured_content = entry[5][0]['content']
        
        found_valid_example = False
        
        for top_level_item in structured_content:
            if isinstance(top_level_item.get('content'), list):
                
                processed_inner_content = []
                inner_content_list = top_level_item.get('content', [])
                
                for item in inner_content_list:
                    if (item.get('tag') == 'div' and 
                        item.get('style', {}).get('fontWeight') == 'bold' and 
                        isinstance(item.get('content'), str)):
                        
                        if not item['content'].startswith("1. "):
                            item['content'] = "1. " + item['content']
                        processed_inner_content.append(item)
                    
                    elif is_example_sentence_with_content(item):
                        if not found_valid_example:
                            processed_inner_content.append(item)
                            found_valid_example = True
                    
                    elif (item.get('tag') == 'details' and 
                          item.get('content') and 
                          item['content'][0].get('content') == 'Example Sentences'):
                        pass
                    
                    else:
                        processed_inner_content.append(item)
                
                top_level_item['content'] = processed_inner_content
            elif top_level_item.get('tag') == 'div' and isinstance(top_level_item.get('content'), list):
                 for span_item in top_level_item['content']:
                    if span_item.get('tag') == 'span' and span_item.get('content') and isinstance(span_item['content'], str):
                         span_item['content'] = span_item['content'].strip()

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
        shutil.copyfile(INPUT_FILE, backup_path)
        print(f"Created backup at: {backup_path}")
        process_term_bank(INPUT_FILE)
    else:
        print(f"Error: '{INPUT_FILE}' not found.")
    
    input("\nPress Enter to close...")
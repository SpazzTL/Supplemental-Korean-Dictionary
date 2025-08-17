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
        
    def update_styles_and_newlines(obj):
        """
        Recursively finds and updates style attributes and replaces newlines.
        """
        if isinstance(obj, dict):
            if 'style' in obj and isinstance(obj['style'], dict):
                style = obj['style']
                if style.get('fontSize') == '0.9em':
                    style['fontSize'] = '1em'
                if style.get('color') == '#444':
                    style['color'] = '#a8a8a8'
            for key, value in obj.items():
                if isinstance(value, str):
                    obj[key] = value.replace('\\n', '\n')
                else:
                    update_styles_and_newlines(value)
        elif isinstance(obj, list):
            for i in range(len(obj)):
                if isinstance(obj[i], str):
                    obj[i] = obj[i].replace('\\n', '\n')
                else:
                    update_styles_and_newlines(obj[i])
    
    # Apply the new style and newline updates
    update_styles_and_newlines(data)
    
    # Existing cleaning logic
    for top_level_list in data:
        if isinstance(top_level_list, list) and len(top_level_list) > 5 and isinstance(top_level_list[5], list):
            for structured_content_item in top_level_list[5]:
                if structured_content_item.get('type') == 'structured-content' and 'content' in structured_content_item:
                    processed_content = []
                    for item in structured_content_item['content']:
                        if is_example_sentence_with_content(item):
                            pass
                        elif item.get('tag') == 'div' and item.get('style') and item['style'].get('fontStyle') == 'italic' and item['content'] == 'Noun':
                            pass
                        else:
                            processed_content.append(item)
                    structured_content_item['content'] = processed_content
    
    for term_list in data:
        if isinstance(term_list, list) and len(term_list) > 5 and isinstance(term_list[5], list):
            for structured_content_item in term_list[5]:
                if structured_content_item.get('type') == 'structured-content' and isinstance(structured_content_item.get('content'), list):
                    for top_level_item in structured_content_item['content']:
                        if top_level_item.get('tag') == 'div' and isinstance(top_level_item.get('content'), list):
                            processed_inner_content = []
                            for item in top_level_item['content']:
                                if item.get('tag') == 'div' and item.get('style') and item['style'].get('fontStyle') == 'italic' and item.get('content') == 'Noun':
                                    continue
                                if item.get('tag') == 'div' and item.get('style') and item['style'].get('fontWeight') == 'bold' and item.get('content') == 'Example Sentences':
                                    continue
                                processed_inner_content.append(item)
                            
                            top_level_item['content'] = processed_inner_content
    
    for top_level_list in data:
        if isinstance(top_level_list, list) and len(top_level_list) > 5 and isinstance(top_level_list[5], list):
            for structured_content_item in top_level_list[5]:
                if structured_content_item.get('type') == 'structured-content' and isinstance(structured_content_item.get('content'), list):
                    processed_content = []
                    for item in structured_content_item['content']:
                        if item.get('tag') == 'details' and item.get('content') and item['content'][0].get('content') == 'Example Sentences':
                            continue
                        processed_content.append(item)
                    structured_content_item['content'] = processed_content

    for top_level_list in data:
        if isinstance(top_level_list, list) and len(top_level_list) > 5 and isinstance(top_level_list[5], list):
            for structured_content_item in top_level_list[5]:
                if structured_content_item.get('type') == 'structured-content' and isinstance(structured_content_item.get('content'), list):
                    top_level_item = structured_content_item['content'][0] if structured_content_item['content'] else None
                    if top_level_item and top_level_item.get('tag') == 'div' and isinstance(top_level_item.get('content'), list):
                        for span_item in top_level_item['content']:
                            if span_item.get('tag') == 'span' and isinstance(span_item.get('content'), str):
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
        try:
            shutil.copy2(INPUT_FILE, backup_path)
            print(f"Created backup of '{INPUT_FILE}' at '{backup_path}'")
        except Exception as e:
            print(f"Error creating backup: {e}")

        process_term_bank(INPUT_FILE)
    else:
        print(f"Error: The file '{INPUT_FILE}' does not exist.")
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import orjson
import os
import re
import zipfile

# --- User-configurable variables ---
OUTPUT_DIRECTORY = "handzip"
# The main file dictionary words will go into.
OUTPUT_FILENAME = "term_bank_1.json"
# What to do if the file already exists. 
EXISTING_FILE_ACTION = "Append"  # Options: "Overwrite", "Append", "Rename"
ZIP_SOURCE_DIRECTORY = "handzip"  # Directory to zip
ZIP_OUTPUT_DIRECTORY = ""  # Directory where the zip file will be saved. Leave empty for script directory.
ZIP_FILENAME = "output.zip"


# --- Script Var ---

# Global variable to store the data of the term being edited
current_term_data = None
# Global variable to store all dictionary data
dictionary_data = []
# Global variable for the definitions structured content
current_definitions = None

# --- Help Text for GUI Fields ---
HELP_TEXT = """
**Field Guide & Examples**


**-- Required Fields --**

- **Term:** The word or phrase you're defining.
  *Example: Hello*

- **Score:** Some kind of ranking number. The script needs a number here, even 0.
  *Example: 0*

- **Definitions (one per line):** The actual meaning of the term. You need at least one line here. For fancier formatting with lists or bold text, use the 'Edit as Structured Content' button.
  *Example: Greeting*

- **Sequence Number:** An ID number for the entry. I honestly don't understand, 1 works well.
  *Example: 1*

**-- Optional Fields (can be left blank) --**

- **Reading:** How to pronounce the term, I guess?
  *Example: hal-o*

- **Definition Tags:** Tags about the definition itself.
  *Example: Adjective*

- **Rule Identifiers:** Used for rule system, I think?
  *Example: adj*

- **Term Tags:** Extra tags for the term, maybe for filtering?
  *Example: common*
"""

# --- Helper functions for structured content ---
def parse_structured_content_to_text(content):
    """Recursively extracts text from structured content for display."""
    text = ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        for item in content:
            text += parse_structured_content_to_text(item) + " "
    elif isinstance(content, dict) and 'content' in content:
        text += parse_structured_content_to_text(content['content'])
    return text.strip()

def add_html_tag(text_widget, tag_name, **attributes):
    """Inserts a new tag into the structured content text box."""
    start = text_widget.index(tk.INSERT)
    # Create the tag representation for display
    attrs_str = " ".join([f'{k}="{v}"' for k, v in attributes.items()])
    tag_start = f'<{tag_name} {attrs_str}>' if attributes else f'<{tag_name}>'
    tag_end = f'</{tag_name}>'
    text_widget.insert(start, tag_start + tag_end)
    # Move cursor inside the new tag
    text_widget.mark_set(tk.INSERT, f"{start}+{len(tag_start)}c")

def show_structured_help():
    """Displays a help pop-up with an example of valid structured JSON for definitions."""
    help_message = """
The Structured Definitions editor requires valid JSON format. This is useful for complex definitions, such as those with lists or nested structures.

**Explanation:**
- The outermost structure must be a list `[]`.
- Each element of the list can be either a simple string or a JSON object.
- A JSON object should have a `"tag"` key (e.g., "ul", "li", "span") and a `"content"` key.
- The `"content"` can be a string or another list of structured objects.
"""
    messagebox.showinfo("Structured Content Help", help_message)

def open_definitions_editor(parent):
    """Opens a new window for editing structured definitions, pre-populating with content if available."""
    global current_definitions
    
    editor_window = tk.Toplevel(parent)
    editor_window.title("Edit Structured Definitions")
    editor_window.geometry("600x500")

    content_frame = tk.Frame(editor_window)
    content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    definitions_editor_text = tk.Text(content_frame, wrap=tk.WORD)
    definitions_editor_text.pack(fill=tk.BOTH, expand=True)

    # The content for the editor is ALWAYS what's in current_definitions.
    # If it's None (like for a new word), we just treat it as an empty list.
    initial_content = current_definitions if current_definitions is not None else []
    
    # Populate the editor with the JSON text of the content.
    json_text = orjson.dumps(initial_content, option=orjson.OPT_INDENT_2).decode('utf-8')
    definitions_editor_text.insert(tk.END, json_text)

    button_frame = tk.Frame(editor_window)
    button_frame.pack(fill=tk.X, padx=10, pady=5)
    
    tk.Button(button_frame, text="Add div", command=lambda: add_html_tag(definitions_editor_text, "div")).pack(side=tk.LEFT)
    tk.Button(button_frame, text="Add span", command=lambda: add_html_tag(definitions_editor_text, "span")).pack(side=tk.LEFT)
    tk.Button(button_frame, text="Add bold", command=lambda: add_html_tag(definitions_editor_text, "span", style='{"fontWeight": "bold"}')).pack(side=tk.LEFT)
    tk.Button(button_frame, text="Add ul/li", command=lambda: add_html_tag(definitions_editor_text, "ul") or add_html_tag(definitions_editor_text, "li")).pack(side=tk.LEFT)
    
    help_button_editor = tk.Button(button_frame, text="Help", command=show_structured_help)
    help_button_editor.pack(side=tk.LEFT, padx=(20, 0))

    def save_and_close():
        global current_definitions
        try:
            content_str = definitions_editor_text.get("1.0", tk.END).strip()
            if content_str:
                current_definitions = orjson.loads(content_str)
            else:
                current_definitions = []
            
            definitions_text_box.delete("1.0", tk.END)
            definitions_text_box.insert(tk.END, f"[Structured Content]\n{parse_structured_content_to_text(current_definitions)}")
            editor_window.destroy()
        except orjson.JSONDecodeError as e:
            messagebox.showerror("Error", f"Invalid JSON format. Please check your syntax.\nDetails: {e}")

    save_button = tk.Button(editor_window, text="Save Definitions", command=save_and_close)
    save_button.pack(pady=5)
    
def create_entry_data():
    """Gathers data from the GUI and formats it to strictly follow the target JSON schema."""
    global current_definitions

    term = term_entry.get()
    reading = reading_entry.get()
    def_tags = definition_tags_entry.get().strip() or "" # Default to empty string
    rule_ids = rule_ids_entry.get().strip() or ""
    score_str = score_entry.get()
    sequence_num_str = sequence_entry.get()
    term_tags = term_tags_entry.get().strip() or ""
    
    definitions_text = definitions_text_box.get("1.0", tk.END).strip()

    if not term or not score_str or not sequence_num_str:
        messagebox.showerror("Error", "Term, Score, and Sequence Number are required.")
        return None
    if not (definitions_text or current_definitions is not None):
        messagebox.showerror("Error", "Definitions are required.")
        return None

    try:
        score = float(score_str)
        sequence_num = int(sequence_num_str)
    except ValueError:
        messagebox.showerror("Error", "Score must be a number and Sequence Number must be an integer.")
        return None
    
    # This block ensures the definitions are always structured correctly.
    final_definitions_content = []
    if current_definitions is not None:
        # User provided structured content via the editor.
        final_definitions_content = current_definitions
    else:
        # User provided simple, line-by-line definitions.
        # Convert each line into a structured object for schema compliance.
        lines = definitions_text.split('\n')
        stripped_lines = [line.strip() for line in lines if line.strip()]
        for line in stripped_lines:
             final_definitions_content.append({"tag": "div", "content": line})

    # This is the required wrapper for the definitions to follow the schema.
    structured_definitions_wrapper = [
        {
            "type": "structured-content",
            "content": final_definitions_content
        }
    ]

    new_entry = [
        term,
        reading,
        def_tags,
        rule_ids,
        score,
        structured_definitions_wrapper,  # Use the new, correctly wrapped structure
        sequence_num,
        term_tags
    ]
    return new_entry

def get_output_path():
    """Determines the correct output path based on the user's settings."""
    output_dir = os.path.join(os.getcwd(), OUTPUT_DIRECTORY) if os.path.exists(OUTPUT_DIRECTORY) else os.getcwd()
    base_path = os.path.join(output_dir, OUTPUT_FILENAME)

    if EXISTING_FILE_ACTION == "Rename" and os.path.exists(base_path):
        filename_without_ext, extension = os.path.splitext(OUTPUT_FILENAME)
        i = 1
        while True:
            new_filename = f"{filename_without_ext}({i}){extension}"
            new_path = os.path.join(output_dir, new_filename)
            if not os.path.exists(new_path):
                return new_path
            i += 1
    return base_path

def save_dictionary_data():
    """Saves the current dictionary_data list to the JSON file."""
    output_path = get_output_path()
    try:
        if not os.path.exists(os.path.dirname(output_path)):
            os.makedirs(os.path.dirname(output_path))
        with open(output_path, 'wb') as f:
            f.write(orjson.dumps(dictionary_data, option=orjson.OPT_INDENT_2))
    except Exception as e:
        messagebox.showerror("Error", f"Could not save JSON file: {e}")
        return False
    return True

def load_dictionary_data():
    """Loads the dictionary data from the JSON file."""
    global dictionary_data
    output_path = get_output_path()
    if os.path.exists(output_path):
        try:
            with open(output_path, 'rb') as f:
                content = f.read()
                if not content:
                    dictionary_data = []
                else:
                    dictionary_data = orjson.loads(content)
        except orjson.JSONDecodeError:
            messagebox.showerror("Error", "Invalid JSON file. Cannot proceed.")
            dictionary_data = []
            return False
    else:
        dictionary_data = []
    return True

def add_word():
    """Adds a new word or saves changes to the custom term bank JSON file."""
    global current_term_data, dictionary_data

    new_entry = create_entry_data()
    if not new_entry:
        return

    if not load_dictionary_data():
         return

    term_to_add = new_entry[0]
    found = False
    for i, entry in enumerate(dictionary_data):
        if entry[0] == term_to_add:
            dictionary_data[i] = new_entry
            messagebox.showinfo("Success", f"'{term_to_add}' updated successfully.")
            found = True
            break
         
    if not found:
        dictionary_data.append(new_entry)
        messagebox.showinfo("Success", f"'{term_to_add}' added successfully.")

    if save_dictionary_data():
        clear_fields()
    
def delete_term():
    """Deletes the selected term from the dictionary data."""
    global dictionary_data, term_tree, term_browser_window
    selected_item = term_tree.selection()
    if not selected_item:
        messagebox.showinfo("Info", "Please select a term to delete.")
        return

    item = term_tree.item(selected_item)
    term_to_delete = item['values'][0]

    if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the term '{term_to_delete}'?"):
        if not load_dictionary_data():
            return
            
        dictionary_data = [entry for entry in dictionary_data if entry[0] != term_to_delete]
        
        if save_dictionary_data():
            messagebox.showinfo("Success", f"'{term_to_delete}' deleted successfully.")
            term_tree.delete(selected_item)
            clear_fields()
            
def clear_fields():
    """Clears all input fields in the GUI."""
    term_entry.delete(0, tk.END)
    reading_entry.delete(0, tk.END)
    definition_tags_entry.delete(0, tk.END)
    rule_ids_entry.delete(0, tk.END)
    score_entry.delete(0, tk.END)
    sequence_entry.delete(0, tk.END)
    term_tags_entry.delete(0, tk.END)
    definitions_text_box.delete("1.0", tk.END)
    
    global current_term_data, current_definitions
    current_term_data = None
    current_definitions = None
    add_button.config(text="Add Word")

def show_help():
    """Displays the help popup with field info."""
    messagebox.showinfo("Help: Field Information", HELP_TEXT)

def zip_dictionary():
    """Zips the dictionary files in the specified directory."""
    zip_source_path = os.path.join(os.getcwd(), ZIP_SOURCE_DIRECTORY)
    if not os.path.exists(zip_source_path):
        messagebox.showerror("Error", f"Source directory '{ZIP_SOURCE_DIRECTORY}' not found.")
        return

    zip_output_path = os.path.join(os.getcwd(), ZIP_OUTPUT_DIRECTORY)
    if not os.path.exists(zip_output_path):
        os.makedirs(zip_output_path)

    zip_file_path = os.path.join(zip_output_path, ZIP_FILENAME)

    try:
        with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(zip_source_path):
                for file in files:
                    if file == "index.json" or re.match(r"term_bank_\d+\.json", file):
                        file_path = os.path.join(root, file)
                        zipf.write(file_path, arcname=file)
        messagebox.showinfo("Success", f"Files zipped successfully to '{zip_file_path}'.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while zipping files: {e}")

def load_term_for_editing(event=None):
    """Loads the selected term into the main GUI for editing, handling the required schema."""
    global current_term_data, current_definitions, term_browser_window
    selected_item = term_tree.selection()
    if not selected_item:
        return
    
    item = term_tree.item(selected_item)
    term_to_load = item['values'][0]

    for term_data in dictionary_data:
        if term_data[0] == term_to_load:
            current_term_data = term_data
            clear_fields()
            
            # Safely populate fields, checking the length of the data list
            term_entry.insert(0, term_data[0])
            if len(term_data) > 1: reading_entry.insert(0, term_data[1] if term_data[1] else "")
            if len(term_data) > 2: definition_tags_entry.insert(0, term_data[2] if term_data[2] else "")
            if len(term_data) > 3: rule_ids_entry.insert(0, term_data[3] if term_data[3] else "")
            if len(term_data) > 4: score_entry.insert(0, str(term_data[4]))
            
            # --- Definitions (Index 5) ---
            definitions_wrapper = term_data[5] if len(term_data) > 5 else []
            definitions_content = []
            
            # Unwrap the content from the schema structure to prepare for the editor
            if (definitions_wrapper and isinstance(definitions_wrapper, list) and
                len(definitions_wrapper) > 0 and isinstance(definitions_wrapper[0], dict) and
                'content' in definitions_wrapper[0]):
                definitions_content = definitions_wrapper[0]['content']
            
            current_definitions = definitions_content
            definitions_text_box.delete("1.0", tk.END)
            definitions_text_box.insert(tk.END, f"[Structured Content]\n{parse_structured_content_to_text(definitions_content)}")
            
            # --- Sequence Number and Term Tags (Indices 6 and 7) ---
            if len(term_data) > 6 and term_data[6] is not None: sequence_entry.insert(0, str(term_data[6]))
            if len(term_data) > 7: term_tags_entry.insert(0, term_data[7] if term_data[7] else "")
            
            add_button.config(text="Save Changes")
            term_browser_window.destroy()
            return
            
def search_terms(event=None):
    """Filters the term list in the browser based on the search query."""
    search_query = search_entry.get().lower()
    term_tree.delete(*term_tree.get_children())
    
    for term_data in dictionary_data:
        term = term_data[0]
        definition_snippet = ""
        # Safely extract definition text for the snippet preview
        if len(term_data) > 5:
            definitions_wrapper = term_data[5]
            if (definitions_wrapper and isinstance(definitions_wrapper, list) and
                len(definitions_wrapper) > 0 and isinstance(definitions_wrapper[0], dict) and
                'content' in definitions_wrapper[0]):
                definition_snippet = parse_structured_content_to_text(definitions_wrapper[0]['content'])[:50]

        tags = term_data[2] or "" if len(term_data) > 2 else ""
        
        if search_query in term.lower() or search_query in definition_snippet.lower() or search_query in tags.lower():
            term_tree.insert('', 'end', values=(term, definition_snippet, tags))

def sort_column(tree, col, reverse):
    """Sort the items in the Treeview by a specific column."""
    l = [(tree.set(k, col), k) for k in tree.get_children('')]
    l.sort(reverse=reverse)
    for index, (val, k) in enumerate(l):
        tree.move(k, '', index)
    tree.heading(col, command=lambda: sort_column(tree, col, not reverse))

def open_term_browser():
    """Opens a new window to browse and select terms for editing."""
    global term_browser_window, dictionary_data, term_tree, search_entry

    if not load_dictionary_data() or not dictionary_data:
        messagebox.showinfo("Info", "Term bank file not found or is empty. Please add a word first.")
        return

    term_browser_window = tk.Toplevel(root)
    term_browser_window.title("Browse Terms")
    term_browser_window.geometry("800x600")

    search_frame = tk.Frame(term_browser_window, padx=10, pady=10)
    search_frame.pack(fill=tk.X)
    
    tk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
    search_entry = tk.Entry(search_frame)
    search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
    search_entry.bind("<KeyRelease>", search_terms) # Search as user types
    
    columns = ("Term", "Definition", "Tags")
    term_tree = ttk.Treeview(term_browser_window, columns=columns, show="headings")
    term_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    for col in columns:
        term_tree.heading(col, text=col, command=lambda _col=col: sort_column(term_tree, _col, False))
        term_tree.column(col, anchor=tk.W, width=100)
    term_tree.column("Definition", width=400)
        
    term_tree.bind('<Double-1>', load_term_for_editing)
    
    # Initially populate with all terms
    search_terms(None)

    button_frame = tk.Frame(term_browser_window, pady=10)
    button_frame.pack()
    
    tk.Button(button_frame, text="Load Selected for Editing", command=load_term_for_editing).pack(side=tk.LEFT, padx=10)
    tk.Button(button_frame, text="Delete Selected Term", command=delete_term).pack(side=tk.LEFT, padx=10)
    tk.Button(button_frame, text="Close", command=term_browser_window.destroy).pack(side=tk.LEFT, padx=10)

# --- GUI Setup ---
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Add/Edit Dictionary Word")

    input_frame = tk.Frame(root, padx=10, pady=10)
    input_frame.pack(fill=tk.BOTH, expand=True)

    labels = [
        "Term:", "Reading:", "Definition Tags (space-separated):",
        "Rule Identifiers (space-separated):", "Score:",
        "Definitions (one per line):", "Sequence Number:",
        "Term Tags (space-separated):"
    ]

    entry_widgets = {}
    for i, label_text in enumerate(labels):
        label = tk.Label(input_frame, text=label_text, anchor='w')
        label.grid(row=i, column=0, sticky='w', pady=2)
        if label_text == "Definitions (one per line):":
            definitions_text_box = tk.Text(input_frame, height=5, width=40)
            definitions_text_box.grid(row=i, column=1, padx=5, pady=2, sticky='ew')
            entry_widgets['definitions'] = definitions_text_box
        else:
            entry = tk.Entry(input_frame, width=40)
            entry.grid(row=i, column=1, padx=5, pady=2, sticky='ew')
            # A bit of a hack to make the dictionary keys cleaner
            clean_label = label_text.split(':')[0].replace(' (space-separated)', '')
            entry_widgets[clean_label] = entry

    edit_definitions_button = tk.Button(input_frame, text="Edit as Structured Content", command=lambda: open_definitions_editor(root))
    edit_definitions_button.grid(row=labels.index("Definitions (one per line):"), column=2, padx=5, pady=2)

    term_entry = entry_widgets["Term"]
    reading_entry = entry_widgets["Reading"]
    definition_tags_entry = entry_widgets["Definition Tags"]
    rule_ids_entry = entry_widgets["Rule Identifiers"]
    score_entry = entry_widgets["Score"]
    sequence_entry = entry_widgets["Sequence Number"]
    term_tags_entry = entry_widgets["Term Tags"]

    button_frame = tk.Frame(root, pady=10)
    button_frame.pack()

    add_button = tk.Button(button_frame, text="Add Word", command=add_word)
    add_button.pack(side=tk.LEFT, padx=10)
    tk.Button(button_frame, text="Clear Fields", command=clear_fields).pack(side=tk.LEFT, padx=10)
    tk.Button(button_frame, text="Help", command=show_help).pack(side=tk.LEFT, padx=10)
    tk.Button(button_frame, text="Zip Dictionary", command=zip_dictionary).pack(side=tk.LEFT, padx=10)
    tk.Button(button_frame, text="Browse/Edit Terms", command=open_term_browser).pack(side=tk.LEFT, padx=10)

    root.mainloop()
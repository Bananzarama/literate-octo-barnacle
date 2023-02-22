import tkinter as tk
from tkinter import ttk

# Masks with explanations
COMMON_MASKS = [
    ("?l", "Any Lowercase letter"),
    ("?u", "Any Uppercase letter"),
    ("?d", "Any Digit"),
    ("?s", "Any Symbol"),
    ("?a", "Any Lowercase letter, uppercase letter, digit, or symbol"),
    ("?l?d", "Any Lowercase letter and digit"),
    ("?u?d", "Any Uppercase letter and digit"),
    ("?b", "Any character (0x00 - 0xff)"),
    ("?h", "Any Lowercase hexadecimal character (0-9, a-f)"),
    ("?H", "Any Uppercase hexadecimal character (0-9, A-F)"),
    ("?t", "Whitespace character (tab, space)"),
    ("?f", "Any printable character (0x20 - 0x7e)"),
    ("?v", "Any vowel (a, e, i, o, u)"),
    ("?c", "Any consonant"),
    ("?p", "Any punctuation character"),
    ("?z", "Any lowercase letter (a-z)"),
    ("?Z", "Any uppercase letter (A-Z)"),
    ("?1", "Any character in the range 0-9"),
    ("?2", "Any character in the range 0-99"),
    ("?3", "Any character in the range 0-999"),
    ("?4", "Any character in the range 0-9999"),
    ("?5", "Any character in the range 0-99999"),
    ("?6", "Any character in the range 0-999999"),
    ("?7", "Any character in the range 0-9999999"),
    ("?8", "Any character in the range 0-99999999"),
    ("?9", "Any character in the range 0-999999999"),
    ("?10", "Any character in the range 0-9999999999"),
]

# Transformation rules with explanations
COMMON_RULES = [
    ("t0", "Append 0 to end"),
    ("t1", "Append 1 to end"),
    ("t2", "Append 2 to end"),
    ("t3", "Append 3 to end"),
    ("t4", "Append 4 to end"),
    ("t5", "Append 5 to end"),
    ("t6", "Append 6 to end"),
    ("t7", "Append 7 to end"),
    ("t8", "Append 8 to end"),
    ("t9", "Append 9 to end"),
    ("ta", "Append a to end"),
    ("tb", "Append b to end"),
    ("tc", "Append c to end"),
    ("td", "Append d to end"),
    ("te", "Append e to end"),
    ("tf", "Append f to end"),
    ("cA", "Capitalize first letter"),
    ("c", "Capitalize all letters"),
    ("r", "Reverse string"),
    ("l", "Make all characters lowercase"),
    ("u", "Make all characters uppercase"),
    ("d", "Duplicate each character"),
    ("f", "Reflect string"),
    ("x", "Swap first two characters"),
    ("X", "Swap last two characters"),
    ("p", "Swap first and last characters"),
    ("q", "Remove first character"),
    ("Q", "Remove last character"),
    ("g", "Toggle the case of each character"),
    ("j", "Add a space between each character"),
    ("k", "Remove all spaces"),
    ("y", "Duplicate first character"),
    ("Y", "Duplicate last character"),
    ("z", "Increment numbers found in string"),
    ("Z", "Decrement numbers found in string"),
    ("m", "Append characters from mask to end of string"),
    ("n", "Prepend characters from mask to beginning of string"),
]

def generate_mask_file():
    selected_masks = [mask[0] for mask in mask_vars if mask[1].get() == 1] # Get the selected masks
    
    mask_string = ""
    for mask in selected_masks:
        mask_string += mask
    
    output_file_name = mask_output_entry.get() + '.hcmask'
    
    with open(output_file_name, "w") as f:
        f.write(mask_string)

def generate_rule_file():
    selected_rules = [rule[0] for rule in rule_vars if rule[1].get() == 1] # Get the selected rules
    
    rule_string = ""
    for rule in selected_rules:
        rule_string += rule + '\n'

    output_file_name = rule_output_entry.get() + '.rule'
    with open(output_file_name, "w") as f:
        f.write(':\n' + rule_string)

root = tk.Tk()
root.title("Hashcat File Generator")

# Set the size of the window
root.geometry("500x500")

# Create a notebook with two tabs
notebook = ttk.Notebook(root)

# Create the first tab for generating .mask files
mask_tab = ttk.Frame(notebook)
notebook.add(mask_tab, text="Generate .mask files")

# Create a label to explain the purpose of the mask checkboxes
mask_label = tk.Label(mask_tab, text="Select one or more mask options:")
mask_label.pack()

# Create a scrollable frame for the mask checkboxes
mask_scroll_frame = tk.Frame(mask_tab)
mask_scroll_frame.pack(fill="both", expand=True)

mask_canvas = tk.Canvas(mask_scroll_frame)
mask_canvas.pack(side="left", fill="both", expand=True)

mask_scrollbar = ttk.Scrollbar(mask_scroll_frame, orient="vertical", command=mask_canvas.yview)
mask_scrollbar.pack(side="right", fill="y")

mask_canvas.configure(yscrollcommand=mask_scrollbar.set)
mask_canvas.bind("<Configure>", lambda e: mask_canvas.configure(scrollregion=mask_canvas.bbox("all")))

mask_frame = tk.Frame(mask_canvas)
mask_canvas.create_window((0, 0), window=mask_frame, anchor="nw")

# Create the checkboxes for the masks
mask_vars = []
for mask, desc in COMMON_MASKS:
    var = tk.IntVar()
    mask_check = tk.Checkbutton(mask_frame, text=desc, variable=var)
    mask_check.pack(anchor="w")
    mask_vars.append((mask, var))

# Create a label and entry box for the output file name
mask_output_label = tk.Label(mask_tab, text="Output file name:")
mask_output_label.pack()
mask_output_entry = tk.Entry(mask_tab)
mask_output_entry.pack()

# Create a button that generates the mask file when clicked
mask_button = tk.Button(mask_tab, text="Generate .mask file", command=generate_mask_file)
mask_button.pack()

# Create the second tab for generating .rule files
rule_tab = ttk.Frame(notebook)
notebook.add(rule_tab, text="Generate .rule files")

# Create a label to explain the purpose of the rule checkboxes
rule_label = tk.Label(rule_tab, text="Select one or more rule options:")
rule_label.pack()

# Create a scrollable frame for the rule checkboxes
rule_scroll_frame = tk.Frame(rule_tab)
rule_scroll_frame.pack(fill="both", expand=True)

rule_canvas = tk.Canvas(rule_scroll_frame)
rule_canvas.pack(side="left", fill="both", expand=True)

rule_scrollbar = ttk.Scrollbar(rule_scroll_frame, orient="vertical", command=rule_canvas.yview)
rule_scrollbar.pack(side="right", fill="y")

rule_canvas.configure(yscrollcommand=rule_scrollbar.set)
rule_canvas.bind("<Configure>", lambda e: rule_canvas.configure(scrollregion=rule_canvas.bbox("all")))

rule_frame = tk.Frame(rule_canvas)
rule_canvas.create_window((0, 0), window=rule_frame, anchor="nw")

# Create the checkboxes for the rules
rule_vars = []
for rule, desc in COMMON_RULES:
    var = tk.IntVar()
    rule_check = tk.Checkbutton(rule_frame, text=desc, variable=var)
    rule_check.pack(anchor="w")
    rule_vars.append((rule, var))

# Create a label and entry box for the output file name
rule_output_label = tk.Label(rule_tab, text="Output file name:")
rule_output_label.pack()
rule_output_entry = tk.Entry(rule_tab)
rule_output_entry.pack()

# Create a button that generates the rule file when clicked
rule_button = tk.Button(rule_tab, text="Generate .rule file", command=generate_rule_file)
rule_button.pack()

notebook.pack(expand=True, fill="both")

root.mainloop()
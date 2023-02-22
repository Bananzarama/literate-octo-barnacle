import tkinter as tk
from tkinter import ttk
import tkinter.filedialog

COMMON_MASKS = [
    ("?l", "Any Lowercase letter"),
    ("?u", "Any Uppercase letter"),
    ("?d", "Any Digit"),
    ("?s", "Any Symbol"),
    ("?a", "Mixed Alpha"),
    ("?v", "Any vowel"),
    ("?c", "Any consonant"),
]

COMMON_RULES = [
    ("cA", "Capitalize first letter"),
    ("c", "Capitalize all letters"),
    ("r", "Reverse string"),
    ("t", "Toggle case"),
    ("d", "Duplicate"),
    ("f", "Reflect"),
]

class HashcatGenerator:
    def __init__(self):
        self.mask_sets = [[]]  # List of character sets for each mask set
        self.current_set_index = 0  # Index of the currently selected mask set
        self.rule_vars = []  # List of variables for each rule checkbox

        self.window = tk.Tk()
        self.window.title("Hashcat Generator")

        # Set the size of the window
        self.window.geometry("500x350")

        # Create a notebook with two tabs
        notebook = ttk.Notebook(self.window)

        # Create the first tab for generating .mask files
        mask_tab = ttk.Frame(notebook)
        notebook.add(mask_tab, text="Generate mask file")
        
        # Create the second tab for generating .rule files
        rule_tab = ttk.Frame(notebook)
        notebook.add(rule_tab, text="Generate rule file")

        # configure the grid
        self.window.rowconfigure(0, weight=1)
        self.window.columnconfigure(0, weight=1)
        notebook.grid(row=0, column=0, sticky=tk.E+tk.W+tk.N+tk.S) 

        # Add mask set frame
        self.mask_set_frame = tk.Frame(mask_tab)
        self.mask_set_frame.grid()

        # Add mask set buttons
        self.add_set_button = tk.Button(mask_tab, text="Add mask set", command=self.add_mask_set)
        self.add_set_button.grid(row=1,column=1)

        # Add seperator 
        self.separator = ttk.Separator(mask_tab, orient='horizontal')
        self.separator.grid(row=2, column=0, columnspan=4, sticky=tk.EW, pady=5)

        # Add browse button, label and greyed display window
        self.browse_mask_button = tk.Button(mask_tab, text="Browse", command=self.browse_mask)
        self.browse_mask_button.grid(row=3,column=3)
        self.browse_mask_label = tk.Label(mask_tab, text="Output Location:")
        self.browse_mask_label.grid(row=3,column=1)
        self.browse_mask_entry = tk.Entry(mask_tab, state="readonly")
        self.browse_mask_entry.grid(row=3,column=2)

        # Add generate button
        self.generate_button = tk.Button(mask_tab, text="Generate mask", command=self.generate_mask)
        self.generate_button.grid(row=4,column=2)

        # Add rule frame
        self.rule_frame = tk.Frame(rule_tab)
        self.rule_frame.grid()

        # Add rule checkboxes
        for i, rule in enumerate(COMMON_RULES):
            var = tk.IntVar()
            chk = tk.Checkbutton(
                self.rule_frame, text=rule[1], variable=var, 
            )
            j=i
            k=0
            if j >= 4:
                j -= 4
                k += 1
            chk.grid(row=j,column=k)
            # Save the variable for later access
            self.rule_vars.append((rule[0], var))
        
        # Add seperator 
        self.separator = ttk.Separator(rule_tab, orient='horizontal')
        self.separator.grid(row=1, column=0, columnspan=3, sticky=tk.EW, pady=5)

        # Add browse button, label and greyed display window
        self.browse_rule_button = tk.Button(rule_tab, text="Browse", command=self.browse_rule)
        self.browse_rule_button.grid(row=2,column=2)
        self.browse_rule_label = tk.Label(rule_tab, text="Output Location:")
        self.browse_rule_label.grid(row=2,column=0)
        self.browse_rule_entry = tk.Entry(rule_tab, state="readonly")
        self.browse_rule_entry.grid(row=2,column=1)

        # Add generate button
        self.generate_button = tk.Button(rule_tab, text="Generate rule", command=self.generate_rule)
        self.generate_button.grid(row=3,column=1, pady=5)

        self.update_mask_set_frame()
        notebook.grid(row=0,column=0)

        self.window.mainloop()

    def browse_mask(self):
        file_path = tkinter.filedialog.asksaveasfilename(defaultextension=".hcmask", filetypes=[("mask file", "*.hcmask")])
        self.browse_mask_entry.config(state="normal")
        self.browse_mask_entry.delete(0, tk.END)
        self.browse_mask_entry.insert(0, file_path)
        self.browse_mask_entry.config(state="readonly")

    def browse_rule(self):
        file_path = tkinter.filedialog.asksaveasfilename(defaultextension=".rule", filetypes=[("rule file", "*.rule")])
        self.browse_rule_entry.config(state="normal")
        self.browse_rule_entry.delete(0, tk.END)
        self.browse_rule_entry.insert(0, file_path)
        self.browse_rule_entry.config(state="readonly")

    def add_mask_set(self):
        """Add a new mask set"""
        self.mask_sets.append([])
        self.current_set_index = len(self.mask_sets) - 1
        self.update_mask_set_frame()

    def remove_mask_set(self):
        """Remove the current mask set"""
        if len(self.mask_sets) > 1:
            del self.mask_sets[self.current_set_index]
            self.current_set_index = min(self.current_set_index, len(self.mask_sets) - 1)
            self.update_mask_set_frame()

    def select_mask_set(self, index):
        """Select a different mask set"""
        self.current_set_index = index
        self.update_mask_set_frame()

    def add_char_set(self, mask_set_index):
        """Add a character set to the specified mask set"""
        mask_set = self.mask_sets[mask_set_index]

        # Create a dialog box to choose the character set
        dialog = CharSetDialog(self.window, COMMON_MASKS)
        self.window.wait_window(dialog.top)

        if dialog.char_set:
            mask_set.append(dialog.char_set)
            self.update_mask_set_frame()

    def remove_char_set(self, char_set):
        """Remove a character set from the current mask set"""
        mask_set = self.mask_sets[self.current_set_index]
        mask_set.remove(char_set)
        self.update_mask_set_frame()

    def delete_mask_set(self, index):
        """Delete a mask set"""
        del self.mask_sets[index]
        self.current_set_index = min(self.current_set_index, len(self.mask_sets) - 1)
        self.update_mask_set_frame()

    def update_mask_set_frame(self):
        """Update the mask set frame to reflect the current mask sets"""
        # Clear the mask set frame
        for widget in self.mask_set_frame.winfo_children():
            widget.destroy()

        # Add the mask set buttons and character set buttons
        for i, mask_set in enumerate(self.mask_sets):
            # Add the mask set button
            button = tk.Button(
                self.mask_set_frame,
                text=f"Mask set {i+1}",
                command=lambda i=i: self.select_mask_set(i),
            )
            button.grid(row=i,column=1,padx=2,pady=2)

            # Add the character set buttons
            length=0
            for j, char_set in enumerate(mask_set):
                char_set_button = tk.Button(
                    self.mask_set_frame,
                    text=char_set[0],
                    command=lambda char_set=char_set: self.remove_char_set(char_set),
                )
                length=j
                char_set_button.grid(row=i,column=length+2,padx=2,pady=2)
                
            # Add the add character set button
            add_char_set_button = tk.Button(
                self.mask_set_frame,
                text="+",
                command=lambda i=i: self.add_char_set(i),
            )
            add_char_set_button.grid(row=i,column=length+3,padx=2,pady=2)

            # Add the delete mask set button
            if len(self.mask_sets) > 1:
                delete_mask_set_button = tk.Button(
                    self.mask_set_frame,
                    text="x",
                    command=lambda i=i: self.delete_mask_set(i),
                )
                delete_mask_set_button.grid(row=i,column=0,padx=2,pady=2)

    def generate_mask(self):
        """Generate the hashcat mask based on the current mask sets"""
        mask = ""
        for mask_set in self.mask_sets:
            for masks in mask_set:
                mask += masks[0]
            mask += '\n'
        output_file_name = self.browse_mask_entry.get()
        with open(output_file_name, "w") as f:
            f.write(mask)
    
    def generate_rule(self):
        """Generate the hashcat rule based on the current selected rules"""
        selected_rules = [rule[0] for rule in self.rule_vars if rule[1].get() == 1] # Get the selected rules
        rule_string = ""
        for rule in selected_rules:
            rule_string += rule + '\n'
        output_file_name = self.browse_rule_entry.get()
        with open(output_file_name, "w") as f:
            f.write(':\n' + rule_string)

class CharSetDialog:
    """Dialog box to choose a character set"""
    def __init__(self, parent, char_sets):
        top = self.top = tk.Toplevel(parent)
        tk.Label(top, text="Choose a character set").grid(row=0,column=1, columnspan=2)
        self.char_set = None
        i=0
        j=1
        for char_set in char_sets:
            tk.Button(top, text=char_set, command=lambda char_set=char_set: self.set_char_set(char_set)).grid(row=j,column=i,padx=2,pady=2)
            i+=1
            if i >= 4:
                i = 0
                j += 1

    def set_char_set(self, char_set):
        """Set the selected character set and close the dialog"""
        self.char_set = char_set
        self.top.destroy()

if __name__ == "__main__":
    HashcatGenerator()
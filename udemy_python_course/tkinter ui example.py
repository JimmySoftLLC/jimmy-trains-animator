import tkinter as tk
from tkinter import ttk

def add_entry():
    first_name = entry1.get()
    last_name = entry2.get()
    email = entry3.get()
    department = department_var.get()
    tree.insert("", "end", values=(first_name, last_name, email, department))
    entry1.delete(0, tk.END)
    entry2.delete(0, tk.END)
    entry3.delete(0, tk.END)
    dropdown.current(0)

def delete_entry():
    selected_item = tree.selection()
    if selected_item:
        tree.delete(selected_item)

def on_row_select(event):
    selected_item = tree.selection()
    if selected_item:
        item_values = tree.item(selected_item[0], "values")
        entry1.delete(0, tk.END)
        entry1.insert(0, item_values[0])
        entry2.delete(0, tk.END)
        entry2.insert(0, item_values[1])
        entry3.delete(0, tk.END)
        entry3.insert(0, item_values[2])
        department_var.set(item_values[3])

def update_entry(event):
    selected_item = tree.selection()
    if selected_item:
        tree.item(selected_item[0], values=(
            entry1.get(),
            entry2.get(),
            entry3.get(),
            department_var.get()
        ))

# Initialize the main window
root = tk.Tk()
root.title("Editable Tkinter Table")
root.geometry("600x400")

# Apply a theme
style = ttk.Style(root)
style.theme_use('clam')

# Create a Notebook widget (tabs container)
notebook = ttk.Notebook(root)
notebook.pack(expand=1, fill="both")

# Create frames for each tab
tab1 = ttk.Frame(notebook)
tab2 = ttk.Frame(notebook)

# Add tabs to the notebook
notebook.add(tab1, text="Data Entry")
notebook.add(tab2, text="Settings")

# Create a table (Treeview widget)
columns = ("First Name", "Last Name", "Email", "Department")
tree = ttk.Treeview(tab1, columns=columns, show='headings')
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=140, anchor="center")

tree.grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")

# Bind selection event to the Treeview
tree.bind("<<TreeviewSelect>>", on_row_select)

# Data Entry Fields
label1 = ttk.Label(tab1, text="First Name:")
label1.grid(row=1, column=0, padx=10, pady=5, sticky="w")
entry1 = ttk.Entry(tab1)
entry1.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

label2 = ttk.Label(tab1, text="Last Name:")
label2.grid(row=2, column=0, padx=10, pady=5, sticky="w")
entry2 = ttk.Entry(tab1)
entry2.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

label3 = ttk.Label(tab1, text="Email:")
label3.grid(row=3, column=0, padx=10, pady=5, sticky="w")
entry3 = ttk.Entry(tab1)
entry3.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

label4 = ttk.Label(tab1, text="Department:")
label4.grid(row=4, column=0, padx=10, pady=5, sticky="w")
department_var = tk.StringVar()
dropdown = ttk.Combobox(tab1, textvariable=department_var)
dropdown['values'] = ("HR", "Finance", "IT", "Marketing")
dropdown.grid(row=4, column=1, padx=10, pady=5, sticky="ew")
dropdown.current(0)

# Buttons
button1 = ttk.Button(tab1, text="Add", command=add_entry)
button1.grid(row=5, column=0, padx=10, pady=10)

button2 = ttk.Button(tab1, text="Delete", command=delete_entry)
button2.grid(row=5, column=1, padx=10, pady=10)

button3 = ttk.Button(tab1, text="Update", command=lambda: update_entry(None))
button3.grid(row=5, column=2, padx=10, pady=10)

# Bind the Enter key to update the entry
entry1.bind("<Return>", update_entry)
entry2.bind("<Return>", update_entry)
entry3.bind("<Return>", update_entry)
dropdown.bind("<Return>", update_entry)

# Sample data for the table
data = [
    ("John", "Doe", "john.doe@example.com", "IT"),
    ("Jane", "Smith", "jane.smith@example.com", "HR"),
    ("Emily", "Jones", "emily.jones@example.com", "Marketing")
]

for item in data:
    tree.insert("", "end", values=item)

# Configure column and row weights to make the UI responsive
tab1.grid_columnconfigure(1, weight=1)
tab1.grid_rowconfigure(0, weight=1)

# ---------------- Tab 2: Settings ---------------- #
label_settings = ttk.Label(tab2, text="Settings Page")
label_settings.grid(row=0, column=0, padx=20, pady=20)

checkbox_var = tk.BooleanVar()
checkbox = ttk.Checkbutton(tab2, text="Enable feature X", variable=checkbox_var)
checkbox.grid(row=1, column=0, padx=20, pady=10)

button_save_settings = ttk.Button(tab2, text="Save Settings", command=lambda: print("Settings saved"))
button_save_settings.grid(row=2, column=0, padx=20, pady=20)

# Run the application
root.mainloop()

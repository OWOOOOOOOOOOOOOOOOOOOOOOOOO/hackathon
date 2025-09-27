# main.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta
import threading
import time
import random
import tkinter.font as tkfont
import ast

THEMES = {
    "dark": {
        "BG_COLOR": "#1a1a1a",
        "ACCENT_COLOR": "#00d4ff",
        "ACTIVE_BTN_BG": "#0088aa",
        "PANEL_BG": "#2a2a2a",
        "CARD_BG": "#333333",
        "TEXT_COLOR": "#ffffff",
        "SECONDARY_TEXT": "#cccccc",
        "BORDER_COLOR": "#444444",
        "HOVER_COLOR": "#555555",
        "SUCCESS_COLOR": "#00ff88",
        "WARNING_COLOR": "#ffaa00",
        "ERROR_COLOR": "#ff4444"
    },
    "light": {
        "BG_COLOR": "#f8f9fa",
        "ACCENT_COLOR": "#007bff",
        "ACTIVE_BTN_BG": "#0056b3",
        "PANEL_BG": "#ffffff",
        "CARD_BG": "#f8f9fa",
        "TEXT_COLOR": "#212529",
        "SECONDARY_TEXT": "#6c757d",
        "BORDER_COLOR": "#dee2e6",
        "HOVER_COLOR": "#e9ecef",
        "SUCCESS_COLOR": "#28a745",
        "WARNING_COLOR": "#ffc107",
        "ERROR_COLOR": "#dc3545"
    }
}

current_theme = "dark" 

# Apply current theme
def apply_theme():
    global BG_COLOR, ACCENT_COLOR, ACTIVE_BTN_BG, PANEL_BG, CARD_BG, TEXT_COLOR, SECONDARY_TEXT, BORDER_COLOR, HOVER_COLOR, SUCCESS_COLOR, WARNING_COLOR, ERROR_COLOR
    theme = THEMES[current_theme]
    BG_COLOR = theme["BG_COLOR"]
    ACCENT_COLOR = theme["ACCENT_COLOR"]
    ACTIVE_BTN_BG = theme["ACTIVE_BTN_BG"]
    PANEL_BG = theme["PANEL_BG"]
    CARD_BG = theme["CARD_BG"]
    TEXT_COLOR = theme["TEXT_COLOR"]
    SECONDARY_TEXT = theme["SECONDARY_TEXT"]
    BORDER_COLOR = theme["BORDER_COLOR"]
    HOVER_COLOR = theme["HOVER_COLOR"]
    SUCCESS_COLOR = theme["SUCCESS_COLOR"]
    WARNING_COLOR = theme["WARNING_COLOR"]
    ERROR_COLOR = theme["ERROR_COLOR"]

# Initialize theme
apply_theme()

HEADER_FONT = ("Segoe UI", 18, "bold")  # More modern font
LABEL_FONT = ("Segoe UI", 11)
ENTRY_FONT = ("Segoe UI", 11)
BUTTON_FONT = ("Segoe UI", 11, "bold")
LISTBOX_FONT = ("Segoe UI", 10)
TIMER_FONT = ("Segoe UI", 16, "bold")
SCHEDULE_BG = BG_COLOR

# Store tasks
tasks = []

# Categories (Now mutable for custom additions)
categories = ["School", "Activity", "Home", "Rest"]

# AI optimization settings
enable_5min_snapping = True  # Toggle for 5-minute interval snapping

def snap_to_5min(dt):
    """Snap a datetime to the nearest 5-minute interval."""
    minutes = dt.minute
    rounded = round(minutes / 5) * 5
    if rounded == 60:
        dt = dt.replace(minute=0, hour=dt.hour + 1)
    else:
        dt = dt.replace(minute=rounded)
    return dt

# Category management variables
selected_category_index = None # Track which category is selected for editing

# Task editing & deletion
selected_task_index = None # Track which task is selected for editing

# Auto-fill and helper functions
def set_current_datetime():
    """Auto-fill current date and time"""
    now = datetime.now()
    start_date_entry.delete(0, tk.END)
    start_date_entry.insert(0, now.strftime("%m%d%Y"))
    start_time_entry.delete(0, tk.END)
    start_time_entry.insert(0, now.strftime("%I:%M"))
    start_am_pm_var.set(now.strftime("%p"))
    # Set end time 1 hour later as default
    end_time = now + timedelta(hours=1)
    end_date_entry.delete(0, tk.END)
    end_date_entry.insert(0, end_time.strftime("%m%d%Y"))
    end_time_entry.delete(0, tk.END)
    end_time_entry.insert(0, end_time.strftime("%I:%M"))
    end_am_pm_var.set(end_time.strftime("%p"))

def add_duration(minutes):
    """Add specified minutes to current start time to set end time"""
    try:
        start_date = start_date_entry.get()
        start_time = start_time_entry.get()
        start_am_pm = start_am_pm_var.get()
        
        if start_date and start_time:
            start_dt = parse_time(start_date, start_time, start_am_pm)
            if start_dt:
                end_dt = start_dt + timedelta(minutes=minutes)
                end_date_entry.delete(0, tk.END)
                end_date_entry.insert(0, end_dt.strftime("%m%d%Y"))
                end_time_entry.delete(0, tk.END)
                end_time_entry.insert(0, end_dt.strftime("%I:%M"))
                end_am_pm_var.set(end_dt.strftime("%p"))
    except:
        pass

def validate_date_format(event):
    """Provide visual feedback for date format"""
    entry = event.widget
    value = entry.get()
    # Simple validation - check if it looks like MMDDYYYY
    if len(value) == 8 and value.isdigit():
        try:
            datetime.strptime(value, "%m%d%Y")
            entry.config(style="Valid.TEntry")
        except:
            entry.config(style="Invalid.TEntry")
    elif len(value) == 0:
        entry.config(style="TEntry")
    else:
        entry.config(style="Invalid.TEntry")

def validate_time_format(event):
    """Provide visual feedback for time format"""
    entry = event.widget
    value = entry.get()
    # Simple validation - check if it looks like HH:MM
    if len(value) == 5 and value[2] == ':':
        try:
            hours, minutes = value.split(':')
            if 1 <= int(hours) <= 12 and 0 <= int(minutes) <= 59:
                entry.config(style="Valid.TEntry")
            else:
                entry.config(style="Invalid.TEntry")
        except:
            entry.config(style="Invalid.TEntry")
    elif len(value) == 0:
        entry.config(style="TEntry")
    else:
        entry.config(style="Invalid.TEntry")

def on_task_select(event):
    global selected_task_index
    selection = task_listbox.curselection()
    if selection:
        idx = selection[0]
        selected_task_index = idx
        task = tasks[idx]
        # Fill the fields with the selected task's data
        task_name_entry.delete(0, tk.END)
        task_name_entry.insert(0, task['name'])
        # Check if the task's category still exists, otherwise default
        if task['category'] in categories:
            category_var.set(task['category'])
        else:
            category_var.set(categories[0] if categories else "No Category")

        start_date_entry.delete(0, tk.END)
        start_date_entry.insert(0, task['start'].strftime("%m%d%Y"))
        start_time_entry.delete(0, tk.END)
        start_time_entry.insert(0, task['start'].strftime("%I:%M"))
        start_am_pm_var.set(task['start'].strftime("%p"))
        end_date_entry.delete(0, tk.END)
        end_date_entry.insert(0, task['end'].strftime("%m%d%Y"))
        end_time_entry.delete(0, tk.END)
        end_time_entry.insert(0, task['end'].strftime("%I:%M"))
        end_am_pm_var.set(task['end'].strftime("%p"))
    else:
        selected_task_index = None

def edit_task():
    global selected_task_index
    if selected_task_index is None:
        messagebox.showwarning("No Selection", "Please select a task to edit.")
        return
    
    # Temporarily remove the old task before validation and adding the new one
    old_task = tasks.pop(selected_task_index)
    
    # Try to add the task (which performs validation)
    if add_task():
        selected_task_index = None
        show_success_message("Task updated successfully!")
    else:
        # If add_task failed (e.g., validation error), re-insert the old task
        tasks.insert(selected_task_index, old_task)
        # Re-sort to maintain order
        tasks.sort(key=lambda x: x["start"])

def delete_task():
    global selected_task_index
    selection = task_listbox.curselection()
    if not selection:
        messagebox.showwarning("No Selection", "Please select a task to delete.")
        return
    
    # Confirm deletion
    task = tasks[selection[0]]
    if messagebox.askyesno("Confirm Delete", f"Delete task '{task['name']}'?"):
        idx = selection[0]
        del tasks[idx]
        update_task_list()
        update_chart()
        update_schedule()
        update_timer_panel()
        selected_task_index = None
        show_success_message("Task deleted successfully!")

def show_success_message(message):
    """Show a brief success message"""
    success_label.config(text=message)
    try:
        success_label.grid(row=6, column=0, columnspan=4, pady=(6, 0), sticky='w')
    except Exception:
        success_label.pack(pady=(5, 0))

    def _hide():
        try:
            success_label.grid_forget()
        except Exception:
            try:
                success_label.pack_forget()
            except Exception:
                pass

    root.after(3000, _hide)

# Function to convert MMDDYYYY and 12-hour time to datetime
def parse_time(date_str, time_str, am_pm):
    try:
        dt = datetime.strptime(date_str + " " + time_str + " " + am_pm, "%m%d%Y %I:%M %p")
        return dt
    except ValueError:
        return None

# Add task function with better error handling
def add_task():
    name = task_name_entry.get().strip()
    category = category_var.get()
    start_date = start_date_entry.get().strip()
    end_date = end_date_entry.get().strip()
    start_time = start_time_entry.get().strip()
    end_time = end_time_entry.get().strip()
    start_am_pm = start_am_pm_var.get()
    end_am_pm = end_am_pm_var.get()

    # Improved validation with specific error messages
    if not name:
        messagebox.showerror("Missing Information", "Please enter a task name.")
        task_name_entry.focus()
        return False
    
    if not categories:
        messagebox.showerror("No Categories", "Please add a category first.")
        return False

    if not start_date:
        messagebox.showerror("Missing Information", "Please enter a start date (MMDDYYYY).")
        start_date_entry.focus()
        return False
        
    if not start_time:
        messagebox.showerror("Missing Information", "Please enter a start time (HH:MM).")
        start_time_entry.focus()
        return False
        
    if not end_date:
        messagebox.showerror("Missing Information", "Please enter an end date (MMDDYYYY).")
        end_date_entry.focus()
        return False
        
    if not end_time:
        messagebox.showerror("Missing Information", "Please enter an end time (HH:MM).")
        end_time_entry.focus()
        return False

    start_dt = parse_time(start_date, start_time, start_am_pm)
    end_dt = parse_time(end_date, end_time, end_am_pm)

    if start_dt is None:
        messagebox.showerror("Invalid Date/Time", "Start date or time is invalid.\nDate format: MMDDYYYY\nTime format: HH:MM")
        start_date_entry.focus()
        return False
    if end_dt is None:
        messagebox.showerror("Invalid Date/Time", "End date or time is invalid.\nDate format: MMDDYYYY\nTime format: HH:MM")
        end_date_entry.focus()
        return False

    # Apply 5-minute snapping if enabled
    if enable_5min_snapping:
        start_dt = snap_to_5min(start_dt)
        end_dt = snap_to_5min(end_dt)

    if end_dt <= start_dt:
        messagebox.showerror("Invalid Time Range", "End time must be after start time.")
        end_time_entry.focus()
        return False

    tasks.append({
        "name": name,
        "category": category,
        "start": start_dt,
        "end": end_dt,
        "duration": (end_dt - start_dt).total_seconds() / 60
    })

    # Sort tasks by start time
    tasks.sort(key=lambda x: x["start"])

    update_task_list()
    update_chart()
    update_schedule()
    update_timer_panel()

    # Clear only the task name, keep time fields for easy sequential entry
    task_name_entry.delete(0, tk.END)
    task_name_entry.focus()  # Focus back on name field
    show_success_message("Task added successfully!")
    
    return True

# Update listbox
def update_task_list():
    task_listbox.delete(0, tk.END)
    # Ensure all task categories still exist
    for task in tasks:
        if task['category'] not in categories:
            task['category'] = categories[0] if categories else "School"

    for task in tasks:
        start_fmt = task['start'].strftime("%m/%d %I:%M %p")
        end_fmt = task['end'].strftime("%I:%M %p")
        # More compact display for better readability
        task_listbox.insert(tk.END, f"{task['name']} ({task['category']}) • {start_fmt} - {end_fmt}")

def update_chart():
    # Sum durations per category
    category_times = {}
    for task in tasks:
        # Only count tasks whose category still exists
        if task["category"] in categories:
            if task["category"] in category_times:
                category_times[task["category"]] += task["duration"]
            else:
                category_times[task["category"]] = task["duration"]

    fig.clear()
    ax = fig.add_subplot(111)
    # Match chart background to app background and use accent color for text
    ax.set_facecolor(BG_COLOR)
    if category_times:
        wedges, texts, autotexts = ax.pie(
            category_times.values(),
            labels=category_times.keys(),
            autopct='%1.1f%%',
            textprops={'fontsize': 10, 'fontname': FONT_FAMILY, 'color': ACCENT_COLOR}
        )
        # Ensure all text elements use the accent color
        for t in list(texts) + list(autotexts):
            t.set_color(ACCENT_COLOR)
        ax.set_title("Time Allocation by Category", fontsize=13, fontweight="bold", fontname=FONT_FAMILY, color=ACCENT_COLOR)
    else:
        # Show an empty pie chart with a "No Data" label using accent color
        # Use a small non-zero value for 'No Data' to ensure the pie chart appears
        ax.pie([1], labels=["No Data"], colors=[BG_COLOR], wedgeprops={'edgecolor': ACCENT_COLOR, 'linewidth': 1, 'antialiased': True})
        # Add text in the middle manually since autopct won't apply well
        ax.text(0, 0, "No Task Data", color=ACCENT_COLOR, fontsize=12, ha='center', va='center')
        ax.set_title("Time Allocation by Category", fontsize=13, fontweight="bold", fontname=FONT_FAMILY, color=ACCENT_COLOR)

    canvas.draw()

# Schedule panel code

def update_schedule():
    schedule_listbox.delete(0, tk.END)
    now = datetime.now()
    future_tasks = []
    current_task = None
    for task in tasks:
        # Make sure current task category still exists before displaying
        if task['category'] not in categories:
             task['category'] = categories[0] if categories else "School"

        if task['start'] <= now < task['end']:
            current_task = task
        elif now < task['start']:
            future_tasks.append(task)
            
    if current_task:
        schedule_listbox.insert(tk.END, f"🟢 NOW: {current_task['name']} ({current_task['category']})")
    else:
        schedule_listbox.insert(tk.END, "🟡 NOW: Free Time")
        
    for task in future_tasks:
        start_fmt = task['start'].strftime("%m/%d %I:%M %p")
        end_fmt = task['end'].strftime("%I:%M %p")
        schedule_listbox.insert(tk.END, f"⏰ {start_fmt}-{end_fmt}: {task['name']} ({task['category']})")

def schedule_updater():
    while True:
        # The update_schedule is called here on the main thread via root.after
        root.after(0, update_schedule)
        time.sleep(30) # Update every 30 seconds

# Timer panel code
def get_current_and_next_task():
    now = datetime.now()
    current = None
    next_task = None
    for task in tasks:
        # Only consider tasks whose category still exists
        if task['category'] in categories:
            if task['start'] <= now < task['end']:
                current = task
            elif now < task['start']:
                if not next_task or task['start'] < next_task['start']:
                    next_task = task
    return current, next_task

def update_timer_panel():
    current, next_task = get_current_and_next_task()
    now = datetime.now()
    if current:
        current_text = f"Current Task: {current['name']} ({current['category']})"
        until = current['end'] - now
        if until.total_seconds() < 0:
            until = timedelta(seconds=0)
        timer_text = f"Ends in: {str(until).split('.')[0]}"
    else:
        current_text = "Current Task: Free Time"
        timer_text = ""
    if next_task:
        until_next = next_task['start'] - now
        if until_next.total_seconds() < 0:
            until_next = timedelta(seconds=0)
        next_text = f"Next: {next_task['name']} ({next_task['category']}) in {str(until_next).split('.')[0]}"
    else:
        next_text = "No more tasks today."

    # Only update the overview timer panel
    timer_label_overview.config(text=current_text)
    timer_countdown_label_overview.config(text=timer_text)
    next_label_overview.config(text=next_text)

def timer_panel_updater():
    while True:
        # The update_timer_panel is called here on the main thread via root.after
        root.after(0, update_timer_panel)
        time.sleep(1)

# Category management functions

def update_category_list():
    category_listbox.delete(0, tk.END)
    for category in categories:
        category_listbox.insert(tk.END, category)
        
    # Update task input combobox
    category_menu.config(values=categories)
    if categories and category_var.get() not in categories:
        category_var.set(categories[0])
    elif not categories:
        category_var.set("")
        
    # Re-validate task list and update other panels
    update_task_list()
    update_chart()
    update_schedule()
    update_timer_panel()

def add_category():
    new_category = category_entry.get().strip()
    if not new_category:
        messagebox.showerror("Error", "Category name cannot be empty.")
        category_entry.focus()
        return
    if new_category in categories:
        messagebox.showwarning("Warning", f"Category '{new_category}' already exists.")
        return
    
    categories.append(new_category)
    category_entry.delete(0, tk.END)
    update_category_list()
    show_success_message(f"Category '{new_category}' added!")
    
def on_category_select(event):
    global selected_category_index
    selection = category_listbox.curselection()
    if selection:
        selected_category_index = selection[0]
        category_name = categories[selected_category_index]
        category_entry.delete(0, tk.END)
        category_entry.insert(0, category_name)
    else:
        selected_category_index = None

def edit_category():
    global selected_category_index
    new_name = category_entry.get().strip()
    if selected_category_index is None:
        messagebox.showwarning("No Selection", "Please select a category to edit.")
        return
    if not new_name:
        messagebox.showerror("Error", "Category name cannot be empty.")
        category_entry.focus()
        return
    if new_name in categories and categories.index(new_name) != selected_category_index:
        messagebox.showwarning("Warning", f"Category '{new_name}' already exists.")
        return

    old_name = categories[selected_category_index]
    categories[selected_category_index] = new_name
    category_entry.delete(0, tk.END)
    
    # Update all tasks that used the old category name
    for task in tasks:
        if task['category'] == old_name:
            task['category'] = new_name
            
    update_category_list()
    selected_category_index = None
    show_success_message(f"Category renamed to '{new_name}'!")

def delete_category():
    global selected_category_index
    selection = category_listbox.curselection()
    if not selection:
        messagebox.showwarning("No Selection", "Please select a category to delete.")
        return
    
    idx = selection[0]
    category_to_delete = categories[idx]
    
    # Confirm deletion
    if messagebox.askyesno("Confirm Delete", f"Delete category '{category_to_delete}'?\nTasks using this category will be moved to the first available category."):
        categories.pop(idx)
        
        # Update tasks: assign a new category (the first available one) or an empty one if no categories remain
        if categories:
            default_category = categories[0]
        else:
            default_category = "School" # Fallback if all categories are deleted
            
        for task in tasks:
            if task['category'] == category_to_delete:
                task['category'] = default_category
                
        selected_category_index = None
        category_entry.delete(0, tk.END)
        update_category_list()
        show_success_message(f"Category '{category_to_delete}' deleted!")

# Keyboard shortcuts
def on_enter_key(event):
    """Handle Enter key in different contexts"""
    widget = event.widget
    if widget == task_name_entry or widget == category_entry:
        if widget == task_name_entry:
            add_task()
        elif widget == category_entry:
            add_category()
    elif widget in [start_date_entry, start_time_entry, end_date_entry, end_time_entry]:
        add_task()

# Main window setup
root = tk.Tk()
root.title("TimeTrackr")
root.configure(bg=BG_COLOR)
root.geometry("1200x700")  # Slightly larger for better UX
root.minsize(1150, 700)
root.resizable(True, True)

# Resolve a usable font family: prefer Montserrat, fallback to common system fonts
available_fonts = set(tkfont.families())
if "Montserrat" in available_fonts:
    FONT_FAMILY = "Montserrat"
elif "Helvetica" in available_fonts:
    FONT_FAMILY = "Helvetica"
elif "Arial" in available_fonts:
    FONT_FAMILY = "Arial"
else:
    # Last resort: pick any available font
    FONT_FAMILY = list(available_fonts)[0] if available_fonts else "TkDefaultFont"

# Rebuild font tuples using resolved family so all widgets are consistent
HEADER_FONT = (FONT_FAMILY, 16, "bold")
LABEL_FONT = (FONT_FAMILY, 11)
ENTRY_FONT = (FONT_FAMILY, 11)
BUTTON_FONT = (FONT_FAMILY, 11, "bold")
# Use a modest listbox font so lists are readable and not oversized
LISTBOX_FONT = (FONT_FAMILY, 11)
TIMER_FONT = (FONT_FAMILY, 14, "bold")

style = ttk.Style()
style.theme_use("clam")
style.configure("TButton", font=BUTTON_FONT, background=ACCENT_COLOR, foreground=BG_COLOR, padding=6)
style.map("TButton",
          background=[("active", ACTIVE_BTN_BG), ("pressed", "#7fd0d7")],
          foreground=[("active", BG_COLOR), ("pressed", BG_COLOR)])

# Modern flat accent button style
style.configure("FlatAccent.TButton", font=BUTTON_FONT, background=ACCENT_COLOR, foreground=BG_COLOR, padding=8, borderwidth=0, relief="flat")
style.map("FlatAccent.TButton",
          background=[("active", ACTIVE_BTN_BG), ("pressed", "#7fd0d7")],
          foreground=[("active", BG_COLOR), ("pressed", BG_COLOR)])

# Quick duration buttons style
style.configure("Duration.TButton", font=(FONT_FAMILY, 9), background=PANEL_BG, foreground=ACCENT_COLOR, padding=4, borderwidth=1)
style.map("Duration.TButton",
          background=[("active", ACCENT_COLOR), ("pressed", ACTIVE_BTN_BG)],
          foreground=[("active", BG_COLOR), ("pressed", BG_COLOR)])

# Visible, futuristic combobox style
style.configure("Accent.TCombobox", font=ENTRY_FONT, fieldbackground=ACCENT_COLOR, background=ACCENT_COLOR, foreground=BG_COLOR, padding=4)
style.map("Accent.TCombobox",
          fieldbackground=[('readonly', ACCENT_COLOR), ('focus', ACTIVE_BTN_BG)],
          background=[('readonly', ACCENT_COLOR), ('focus', ACTIVE_BTN_BG)],
          foreground=[('readonly', BG_COLOR), ('focus', BG_COLOR)])

# Entry validation styles
style.configure("Valid.TEntry", font=ENTRY_FONT, fieldbackground="#e6ffe6", foreground=BG_COLOR)
style.configure("Invalid.TEntry", font=ENTRY_FONT, fieldbackground="#ffe6e6", foreground=BG_COLOR)

# Make labels use the accent color for text on the dark background
style.configure("TLabel", background=PANEL_BG, foreground=ACCENT_COLOR, font=LABEL_FONT)
# Entries and comboboxes should also use the accent color for text and dark field backgrounds
style.configure("TEntry", font=ENTRY_FONT, fieldbackground=BG_COLOR, foreground=ACCENT_COLOR)
style.configure("TCombobox", font=ENTRY_FONT, fieldbackground=BG_COLOR, foreground=ACCENT_COLOR)
# Frames and labeled frames get a slightly different panel background to add depth
style.configure("TFrame", background=PANEL_BG)
style.configure("TLabelframe", background=PANEL_BG, bordercolor=PANEL_BG)
style.configure("TLabelframe.Label", background=PANEL_BG, foreground=ACCENT_COLOR, font=HEADER_FONT)

# Left side: inputs, tasks & categories
left_frame = tk.Frame(root, bg=PANEL_BG, padx=20, pady=20)
left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Split container for Add view: left column for inputs/categories, right column for today's tasks
add_split_frame = tk.Frame(left_frame, bg=PANEL_BG)
left_col = tk.Frame(add_split_frame, bg=PANEL_BG)
right_col = tk.Frame(add_split_frame, bg=PANEL_BG)

# Category management group
category_group = ttk.LabelFrame(left_frame, text="Category Manager", padding=15)
# Note: don't pack here - we will pack into the split layout when showing Add page
category_group.configure(style='TLabelframe')

category_input_frame = tk.Frame(category_group, bg=PANEL_BG)
category_input_frame.pack(fill=tk.X, pady=(0, 8))

ttk.Label(category_input_frame, text="Category Name:").pack(side=tk.LEFT, pady=4, padx=(0, 8))
category_entry = ttk.Entry(category_input_frame, width=15)
category_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, pady=4, padx=(0, 8))
category_entry.bind('<Return>', on_enter_key)
add_category_btn = ttk.Button(category_input_frame, text="Add", command=add_category, style='FlatAccent.TButton')
add_category_btn.pack(side=tk.LEFT, pady=4)

# Category list with scrollbar
category_frame = tk.Frame(category_group, bg=PANEL_BG)
category_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=(0, 8))
category_listbox = tk.Listbox(
    category_frame,
    font=LISTBOX_FONT,
    height=6,
    bd=0,
    highlightthickness=0,
    relief=tk.FLAT,
    selectbackground=ACTIVE_BTN_BG,
    selectforeground=BG_COLOR,
    bg=BG_COLOR,
    fg=ACCENT_COLOR,
    highlightbackground=ACCENT_COLOR,
    yscrollcommand=lambda f, l: None
)
category_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
category_scrollbar = tk.Scrollbar(category_frame, command=category_listbox.yview, troughcolor=PANEL_BG, bg=PANEL_BG, activebackground=ACCENT_COLOR)
category_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
category_listbox.config(yscrollcommand=category_scrollbar.set)
category_listbox.bind("<<ListboxSelect>>", on_category_select)

category_btn_frame = tk.Frame(category_group, bg=PANEL_BG)
# Move buttons to the bottom of the category manager
category_btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(8, 0))

edit_category_btn = ttk.Button(category_btn_frame, text="Edit", command=edit_category, style='FlatAccent.TButton')
edit_category_btn.pack(side=tk.LEFT, padx=(0, 8), fill=tk.X, expand=True)
delete_category_btn = ttk.Button(category_btn_frame, text="Delete", command=delete_category, style='FlatAccent.TButton')
delete_category_btn.pack(side=tk.LEFT, fill=tk.X, expand=True)

# Input group
input_group = ttk.LabelFrame(left_frame, text="Quick Add Task", padding=15)
input_group.configure(style='TLabelframe')

# Success message label (hidden by default)
success_label = tk.Label(input_group, text="", font=(FONT_FAMILY, 10), bg=PANEL_BG, fg="#90EE90")

# Row 0: Task Name (full width)
ttk.Label(input_group, text="Task Name:").grid(row=0, column=0, sticky="w", pady=(0, 4))
task_name_entry = ttk.Entry(input_group, width=35)
task_name_entry.grid(row=0, column=1, columnspan=3, sticky="ew", pady=(0, 4))
task_name_entry.bind('<Return>', on_enter_key)

# Row 1: Category
ttk.Label(input_group, text="Category:").grid(row=1, column=0, sticky="w", pady=4)
category_var = tk.StringVar(value=categories[0] if categories else "")
category_menu = ttk.Combobox(input_group, textvariable=category_var, values=categories, state="readonly", width=20, style='Accent.TCombobox')
category_menu.grid(row=1, column=1, columnspan=2, sticky="ew", pady=4, padx=(0, 8))

# Inline category controls (compact, for Add Tasks screen)
inline_category_frame = tk.Frame(input_group, bg=PANEL_BG)
inline_category_frame.grid(row=1, column=3, sticky="w", pady=4)

inline_category_entry = ttk.Entry(inline_category_frame, width=12)
inline_category_entry.pack(side=tk.TOP, pady=(0,4))

def add_category_inline():
    new_cat = inline_category_entry.get().strip()
    if not new_cat:
        messagebox.showerror("Error", "Category name cannot be empty.")
        inline_category_entry.focus()
        return
    if new_cat in categories:
        messagebox.showwarning("Warning", f"Category '{new_cat}' already exists.")
        return
    categories.append(new_cat)
    inline_category_entry.delete(0, tk.END)
    update_category_list()
    show_success_message(f"Category '{new_cat}' added!")

def rename_selected_category_inline():
    sel = category_var.get()
    new_name = inline_category_entry.get().strip()
    if not sel:
        messagebox.showwarning("No Selection", "Please select a category to rename.")
        return
    if not new_name:
        messagebox.showerror("Error", "New category name cannot be empty.")
        inline_category_entry.focus()
        return
    try:
        idx = categories.index(sel)
    except ValueError:
        messagebox.showerror("Error", "Selected category no longer exists.")
        return
    if new_name in categories and categories.index(new_name) != idx:
        messagebox.showwarning("Warning", f"Category '{new_name}' already exists.")
        return
    old = categories[idx]
    categories[idx] = new_name
    for task in tasks:
        if task['category'] == old:
            task['category'] = new_name
    inline_category_entry.delete(0, tk.END)
    update_category_list()
    show_success_message(f"Category renamed to '{new_name}'!")

def delete_selected_category_inline():
    sel = category_var.get()
    if not sel:
        messagebox.showwarning("No Selection", "Please select a category to delete.")
        return
    if messagebox.askyesno("Confirm Delete", f"Delete category '{sel}'?\nTasks using this category will be moved to the first available category."):
        try:
            idx = categories.index(sel)
        except ValueError:
            messagebox.showerror("Error", "Selected category no longer exists.")
            return
        categories.pop(idx)
        # Reassign tasks
        default = categories[0] if categories else "School"
        for task in tasks:
            if task['category'] == sel:
                task['category'] = default
        update_category_list()
        show_success_message(f"Category '{sel}' deleted!")

# Inline buttons for category
inline_btns_frame = tk.Frame(inline_category_frame, bg=PANEL_BG)
inline_btns_frame.pack(side=tk.TOP)
ttk.Button(inline_btns_frame, text="Add", command=add_category_inline, style='Duration.TButton').pack(side=tk.LEFT, padx=2)
ttk.Button(inline_btns_frame, text="Rename", command=rename_selected_category_inline, style='Duration.TButton').pack(side=tk.LEFT, padx=2)
ttk.Button(inline_btns_frame, text="Delete", command=delete_selected_category_inline, style='Duration.TButton').pack(side=tk.LEFT, padx=2)

# Row 2: Start Date and Time
ttk.Label(input_group, text="Start Date (MMDDYYYY):").grid(row=2, column=0, sticky="w", pady=4)
start_date_entry = ttk.Entry(input_group, width=12)
start_date_entry.grid(row=2, column=1, sticky="w", pady=4, padx=(0, 8))
start_date_entry.bind('<KeyRelease>', validate_date_format)
start_date_entry.bind('<Return>', on_enter_key)

ttk.Label(input_group, text="Time:").grid(row=2, column=2, sticky="w", pady=4, padx=(8, 4))
start_time_frame = tk.Frame(input_group, bg=PANEL_BG)
start_time_frame.grid(row=2, column=3, sticky="w", pady=4)

start_time_entry = ttk.Entry(start_time_frame, width=8)
start_time_entry.pack(side=tk.LEFT, padx=(0, 4))
start_time_entry.bind('<KeyRelease>', validate_time_format)
start_time_entry.bind('<Return>', on_enter_key)

start_am_pm_var = tk.StringVar(value="AM")
start_am_pm_menu = ttk.Combobox(start_time_frame, textvariable=start_am_pm_var, values=["AM", "PM"], width=4, state="readonly", style='Accent.TCombobox')
start_am_pm_menu.pack(side=tk.LEFT)

# Move 'Now' quick-fill button here so it's aligned with start date/time
now_btn = ttk.Button(start_time_frame, text="Now", command=set_current_datetime, style='Duration.TButton')
now_btn.pack(side=tk.LEFT, padx=(6,0))

# Row 3: End Date and Time
ttk.Label(input_group, text="End Date (MMDDYYYY):").grid(row=3, column=0, sticky="w", pady=4)
end_date_entry = ttk.Entry(input_group, width=12)
end_date_entry.grid(row=3, column=1, sticky="w", pady=4, padx=(0, 8))
end_date_entry.bind('<KeyRelease>', validate_date_format)
end_date_entry.bind('<Return>', on_enter_key)

ttk.Label(input_group, text="Time:").grid(row=3, column=2, sticky="w", pady=4, padx=(8, 4))
end_time_frame = tk.Frame(input_group, bg=PANEL_BG)
end_time_frame.grid(row=3, column=3, sticky="w", pady=4)

end_time_entry = ttk.Entry(end_time_frame, width=8)
end_time_entry.pack(side=tk.LEFT, padx=(0, 4))
end_time_entry.bind('<KeyRelease>', validate_time_format)
end_time_entry.bind('<Return>', on_enter_key)

end_am_pm_var = tk.StringVar(value="AM")
end_am_pm_menu = ttk.Combobox(end_time_frame, textvariable=end_am_pm_var, values=["AM", "PM"], width=4, state="readonly", style='Accent.TCombobox')
end_am_pm_menu.pack(side=tk.LEFT)

# Row 4: Quick Duration Buttons
duration_frame = tk.Frame(input_group, bg=PANEL_BG)
duration_frame.grid(row=4, column=0, columnspan=4, pady=(8, 0))

ttk.Label(duration_frame, text="Quick Duration:", background=PANEL_BG).pack(side=tk.LEFT, padx=(0, 8))
ttk.Button(duration_frame, text="15min", command=lambda: add_duration(15), style='Duration.TButton').pack(side=tk.LEFT, padx=(0, 4))
ttk.Button(duration_frame, text="30min", command=lambda: add_duration(30), style='Duration.TButton').pack(side=tk.LEFT, padx=(0, 4))
ttk.Button(duration_frame, text="1hr", command=lambda: add_duration(60), style='Duration.TButton').pack(side=tk.LEFT, padx=(0, 4))
ttk.Button(duration_frame, text="2hr", command=lambda: add_duration(120), style='Duration.TButton').pack(side=tk.LEFT, padx=(0, 4))
ttk.Button(duration_frame, text="Custom", command=lambda: messagebox.showinfo("Custom Duration", "Enter start time, then use the time fields to set your end time."), style='Duration.TButton').pack(side=tk.LEFT)

# Row 5: Add/Edit Task Buttons
button_frame = tk.Frame(input_group, bg=PANEL_BG)
button_frame.grid(row=5, column=0, columnspan=4, pady=(12, 0), sticky="ew")

add_btn = ttk.Button(button_frame, text="Add Task", command=add_task, style='FlatAccent.TButton')
add_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))

edit_task_btn = ttk.Button(button_frame, text="Update Task", command=edit_task, style='FlatAccent.TButton')
edit_task_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 0))
edit_task_btn.pack_forget()  # Hide initially

def show_add_buttons(event=None):
    if task_listbox.curselection():
        add_btn.pack_forget()
        edit_task_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
    else:
        edit_task_btn.pack_forget()
        add_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))

# Configure grid weights for responsive layout
for i in range(4):
    input_group.columnconfigure(i, weight=1)
# Give vertical space so fields spread out when the input_group expands
for r in range(6):
    try:
        input_group.rowconfigure(r, weight=1)
    except:
        pass

# Task list group
task_list_group = ttk.LabelFrame(left_frame, text="Today's Tasks", padding=12)
task_list_group.configure(style='TLabelframe')

# Add scrollbar for task list
task_frame = tk.Frame(task_list_group, bg=PANEL_BG)
task_frame.pack(fill=tk.BOTH, expand=True)

task_scrollbar = tk.Scrollbar(task_frame, troughcolor=PANEL_BG, bg=PANEL_BG, activebackground=ACCENT_COLOR)
task_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

task_listbox = tk.Listbox(
    task_frame,
    font=LISTBOX_FONT,
    height=6,  # Reduced height for better proportions
    bd=0,
    highlightthickness=0,
    relief=tk.FLAT,
    selectbackground=ACTIVE_BTN_BG,
    selectforeground=BG_COLOR,
    bg=BG_COLOR,
    fg=ACCENT_COLOR,
    highlightbackground=ACCENT_COLOR,
    yscrollcommand=task_scrollbar.set
)
task_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
task_scrollbar.config(command=task_listbox.yview)

task_listbox.bind("<<ListboxSelect>>", lambda e: (on_task_select(e), show_add_buttons(e)))
task_listbox.bind("<ButtonRelease-1>", show_add_buttons)

# Task action buttons
task_btn_frame = tk.Frame(task_list_group, bg=PANEL_BG)
task_btn_frame.pack(fill=tk.X, pady=(8, 0))

delete_btn = ttk.Button(task_btn_frame, text="Delete Task", command=delete_task, style='FlatAccent.TButton')
delete_btn.pack(fill=tk.X)

# Overview section (pie chart + task timer)
# Make overview a top-level section so it can be shown full-screen independent of the Add UI
overview_frame = ttk.LabelFrame(root, text="Overview", padding=15)
overview_frame.configure(style='TLabelframe')

# Create a subframe to hold pie chart and timer side by side
bottom_frame = tk.Frame(overview_frame, bg=PANEL_BG)
bottom_frame.pack(fill=tk.BOTH, expand=True)

# Pie chart on the left
pie_frame = tk.Frame(bottom_frame, bg=BG_COLOR)
pie_frame.pack(side=tk.LEFT, padx=(0, 20), pady=10)

fig = plt.Figure(figsize=(4, 4), facecolor=BG_COLOR)
canvas = FigureCanvasTkAgg(fig, master=pie_frame)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
fig.tight_layout()

# Task timer panel on the right
timer_overview_frame = tk.Frame(bottom_frame, bg=BG_COLOR)
timer_overview_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=10)

timer_label_overview = tk.Label(
    timer_overview_frame,
    text="Current Task: Free Time",
    font=TIMER_FONT,
    bg=BG_COLOR,
    fg=ACCENT_COLOR,
    anchor="center",
    justify="center",
    wraplength=250
)
timer_label_overview.pack(anchor="center", pady=(20, 0), fill="x")

timer_countdown_label_overview = tk.Label(
    timer_overview_frame,
    text="",
    font=TIMER_FONT,
    bg=BG_COLOR,
    fg=ACCENT_COLOR,
    anchor="center",
    justify="center"
)
timer_countdown_label_overview.pack(anchor="center", pady=(10, 0), fill="x")

next_label_overview = tk.Label(
    timer_overview_frame,
    text="",
    font=LABEL_FONT,
    bg=BG_COLOR,
    fg=ACCENT_COLOR,
    anchor="center",
    justify="center",
    wraplength=250
)
next_label_overview.pack(anchor="center", pady=(15, 0), fill="x")

# Right side: schedule panel
side_frame = tk.Frame(root, bg=SCHEDULE_BG, bd=0, relief=tk.FLAT)
side_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 20), pady=20)

schedule_header = tk.Label(side_frame, text="Today's Schedule", font=HEADER_FONT, bg=SCHEDULE_BG, fg=ACCENT_COLOR)
schedule_header.pack(pady=(0, 15), anchor="center")

# Schedule with improved scrollbar
schedule_frame = tk.Frame(side_frame, bg=SCHEDULE_BG)
schedule_frame.pack(fill=tk.BOTH, expand=True)

schedule_scrollbar = tk.Scrollbar(schedule_frame, troughcolor=PANEL_BG, bg=PANEL_BG, activebackground=ACCENT_COLOR, width=16)
schedule_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

schedule_listbox = tk.Listbox(
    schedule_frame,
    width=40,
    height=20,
    font=LISTBOX_FONT,
    bg=BG_COLOR,
    fg=ACCENT_COLOR,
    bd=0,
    highlightthickness=0,
    relief=tk.FLAT,
    selectbackground=ACCENT_COLOR,
    selectforeground=BG_COLOR,
    yscrollcommand=schedule_scrollbar.set
)
schedule_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
schedule_scrollbar.config(command=schedule_listbox.yview)

# Navigation / pages
nav_frame = tk.Frame(root, bg=PANEL_BG, height=50)
nav_frame.pack_forget()

def show_start():
    # Hide main UI frames
    for frame in [left_frame, side_frame, nav_frame, overview_frame, add_split_frame]:
        try:
            frame.pack_forget()
        except Exception as e:
            print(f"Warning hiding frame: {e}")
    # Show start screen
    start_frame.pack(fill=tk.BOTH, expand=True)

def hide_start():
    start_frame.pack_forget()

def show_add_page():
    hide_start()
    # Show navigation bar with Back button
    nav_frame.pack(fill=tk.X, pady=(0, 10))
    back_btn.pack(side=tk.LEFT, padx=20, pady=10)
    
    # Show main panels
    left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    side_frame.pack(side=tk.RIGHT, fill=tk.Y)
    # Pack split frame and arrange columns
    add_split_frame.pack(fill=tk.BOTH, expand=True)
    # Make left and right columns share space evenly
    left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
    right_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    left_col.update()
    right_col.update()
    # Place input_group in left_col and task_list_group in right_col
    try:
        # Ensure category manager is hidden on Add page
        try:
            category_group.pack_forget()
        except Exception as e:
            print(f"Warning hiding category_group: {e}")
        # Category manager intentionally omitted from Add page (moved to Edit Categories page)
        # Let input_group take the full height of the left column
        input_group.pack(in_=left_col, fill=tk.BOTH, expand=True, pady=(0, 15))
        # Make task list fill the right column
        task_list_group.pack(in_=right_col, fill=tk.BOTH, expand=True, pady=(0, 15))
    except Exception:
        pass
    # Ensure overview is hidden while in Add view so it doesn't appear inside the Add layout
    try:
        overview_frame.pack_forget()
    except:
        pass

def show_category_page():
    """Show a categories-only page with back navigation."""
    hide_start()
    # Show navigation bar with Back button
    nav_frame.pack(fill=tk.X, pady=(0, 10))
    back_btn.pack(side=tk.LEFT, padx=20, pady=10)

    # Show only the left_frame area so category manager can be focused
    left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    # Hide other panels
    try:
        side_frame.pack_forget()
    except:
        pass

    # Ensure split frame is not shown; place category_group directly in left_frame
    try:
        add_split_frame.pack_forget()
    except Exception as e:
        print(f"Warning hiding add_split_frame: {e}")

    try:
        # Place the category_group to occupy the full left area
        category_group.pack(fill=tk.BOTH, expand=True, padx=20, pady=(20, 15))
        # Hide other input/task groups while editing categories
        input_group.pack_forget()
        task_list_group.pack_forget()
    except:
        pass

    # Focus the category entry for quick editing
    try:
        category_entry.focus()
    except:
        pass
    
    # Ensure overview is hidden while editing categories
    try:
        overview_frame.pack_forget()
    except:
        pass

def show_overview_page():
    hide_start()
    nav_frame.pack(fill=tk.X, pady=(0, 10))
    back_btn.pack(side=tk.LEFT, padx=20, pady=10)
    # Hide other panels and show the overview as a full-window view
    try:
        left_frame.pack_forget()
    except:
        pass
    try:
        side_frame.pack_forget()
    except:
        pass

    for widget in [category_group, input_group, task_list_group, add_split_frame]:
        try:
            widget.pack_forget()
        except:
            pass

    try:
        overview_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        # Ensure inner frames expand properly
        try:
            bottom_frame.pack(fill=tk.BOTH, expand=True)
            pie_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20), pady=10)
            timer_overview_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=10)
        except:
            pass
    except Exception as e:
        print(f"Warning showing overview: {e}")

# Start screen frame
start_frame = tk.Frame(root, bg=BG_COLOR)

# Centered content
start_content = tk.Frame(start_frame, bg=BG_COLOR)
start_content.pack(expand=True, fill=tk.BOTH)

title_label = tk.Label(start_content, text="TimeTrackr", font=(FONT_FAMILY, 40, "bold"), bg=BG_COLOR, fg=ACCENT_COLOR)
title_label.pack(pady=(100, 15))

subtitle_label = tk.Label(start_content, text="Manage your daily tasks efficiently", font=(FONT_FAMILY, 14), bg=BG_COLOR, fg=ACCENT_COLOR)
subtitle_label.pack(pady=(0, 40))

start_btn_frame = tk.Frame(start_content, bg=BG_COLOR)
start_btn_frame.pack()

# Next break countdown label on the start screen
next_break_label = tk.Label(start_content, text="Next break: Available now", font=(FONT_FAMILY, 11), bg=BG_COLOR, fg=ACCENT_COLOR)
next_break_label.pack(pady=(6,12))

# AI Assistant helpers (simple local heuristics)
def auto_categorize_tasks():
    """Auto-assign categories to existing tasks using simple keyword matching."""
    mapping = {
        "School": ["homework", "assignment", "study", "lecture", "exam", "math", "science", "history", "english", "class", "test", "quiz", "read", "write", "research"],
        "Activity": ["gym", "exercise", "run", "practice", "sports", "workout", "yoga", "dance", "walk", "bike", "swim", "play"],
        "Home": ["cook", "clean", "laundry", "dishes", "chores", "shop", "grocery", "meal", "garden", "repair", "organize"],
        "Rest": ["nap", "sleep", "rest", "break", "relax", "meditate", "watch", "listen", "hobby"]
    }
    changed = 0
    for task in tasks:
        name = task['name'].lower()
        for cat, keywords in mapping.items():
            if any(k in name for k in keywords):
                if task['category'] != cat:
                    task['category'] = cat
                    changed += 1
                break
    if changed:
        update_category_list()
        show_success_message(f"Auto-categorized {changed} task(s).")
    else:
        messagebox.showinfo("AI Assistant", "No tasks matched keywords for auto-categorization.")

def suggest_time_for_task(name, duration_minutes):
    """Find earliest free slot today with at least duration_minutes available."""
    now = datetime.now()
    today_start = datetime(now.year, now.month, now.day, 0, 0)
    today_end = datetime(now.year, now.month, now.day, 23, 59)
    intervals = []
    for t in tasks:
        if t['end'] < today_start or t['start'] > today_end:
            continue
        s = max(t['start'], today_start)
        e = min(t['end'], today_end)
        intervals.append((s, e))
    intervals.sort(key=lambda x: x[0])
    merged = []
    for s, e in intervals:
        if not merged or s > merged[-1][1]:
            merged.append([s, e])
        else:
            if e > merged[-1][1]:
                merged[-1][1] = e
    search_start = now
    for s, e in merged:
        if (s - search_start).total_seconds() >= duration_minutes * 60:
            return (snap_to_5min(search_start), snap_to_5min(search_start + timedelta(minutes=duration_minutes)))
        if e > search_start:
            search_start = e
    if (today_end - search_start).total_seconds() >= duration_minutes * 60:
        return (snap_to_5min(search_start), snap_to_5min(search_start + timedelta(minutes=duration_minutes)))
    return None

def suggest_time_for_task_interactive():
    name = simpledialog.askstring("AI Assistant", "Task name:")
    if not name:
        return
    minutes = simpledialog.askinteger("AI Assistant", "Duration (minutes):", minvalue=1, initialvalue=60)
    if not minutes:
        return
    suggestion = suggest_time_for_task(name, minutes)
    if suggestion:
        start_dt, end_dt = suggestion
        msg = f"Suggested slot:\n{start_dt.strftime('%m/%d %I:%M %p')} - {end_dt.strftime('%I:%M %p')}"
        if messagebox.askyesno("AI Assistant - Suggestion", msg + "\n\nAdd this task now?"):
            show_add_page()
            task_name_entry.delete(0, tk.END)
            task_name_entry.insert(0, name)
            start_date_entry.delete(0, tk.END)
            start_date_entry.insert(0, start_dt.strftime('%m%d%Y'))
            start_time_entry.delete(0, tk.END)
            start_time_entry.insert(0, start_dt.strftime('%I:%M'))
            start_am_pm_var.set(start_dt.strftime('%p'))
            end_date_entry.delete(0, tk.END)
            end_date_entry.insert(0, end_dt.strftime('%m%d%Y'))
            end_time_entry.delete(0, tk.END)
            end_time_entry.insert(0, end_dt.strftime('%I:%M'))
            end_am_pm_var.set(end_dt.strftime('%p'))
    else:
        messagebox.showinfo("AI Assistant", "No available slot of that duration was found today.")

def parse_duration(dur_str):
    import re
    total_minutes = 0.0
    matches = re.findall(r'(\d+)([dhms])', dur_str.lower())
    for num, unit in matches:
        num = int(num)
        if unit == 'd':
            total_minutes += num * 24 * 60
        elif unit == 'h':
            total_minutes += num * 60
        elif unit == 'm':
            total_minutes += num
        elif unit == 's':
            total_minutes += num / 60.0
    return total_minutes if total_minutes > 0 else None

def generate_schedule_from_text():
    text = simpledialog.askstring("AI Assistant", "Enter tasks (e.g., 'Study math 2h, Exercise 1h55m'):")
    if not text:
        return
    parts = [p.strip() for p in text.split(',')]
    added = 0
    default_category = categories[0] if categories else "School"
    for part in parts:
        if ' ' in part:
            name, dur_str = part.rsplit(' ', 1)
            minutes = parse_duration(dur_str)
            if minutes is None:
                continue
            suggestion = suggest_time_for_task(name, minutes)
            if suggestion:
                start_dt, end_dt = suggestion
                new_task = {
                    "name": name,
                    "category": default_category,
                    "start": start_dt,
                    "end": end_dt,
                    "duration": minutes
                }
                tasks.append(new_task)
                added += 1
    if added:
        tasks.sort(key=lambda x: x["start"])
        update_task_list()
        update_chart()
        update_schedule()
        update_timer_panel()
        show_success_message(f"Added {added} tasks from text!")
    else:
        messagebox.showinfo("AI Assistant", "No tasks added from the input.")

def optimize_schedule():
    if not tasks:
        messagebox.showinfo("AI Assistant", "No tasks to optimize.")
        return
    now = datetime.now()
    today_start = datetime(now.year, now.month, now.day, 8, 0)  # Start at 8 AM
    current_time = max(now, today_start)
    # Sort tasks by original start time
    tasks.sort(key=lambda x: x["start"])
    for task in tasks:
        # Place task at current_time
        task["start"] = current_time
        task["end"] = current_time + timedelta(minutes=task["duration"])
        # Apply 5-minute snapping if enabled
        if enable_5min_snapping:
            task["start"] = snap_to_5min(task["start"])
            task["end"] = snap_to_5min(task["end"])
        current_time = task["end"]
    update_task_list()
    update_chart()
    update_schedule()
    update_timer_panel()
    messagebox.showinfo("AI Assistant", "Schedule optimized: Tasks packed sequentially starting from 8 AM or now.")


# Homework chat assistant (local + optional LLM)
def safe_eval_expr(expr):
    """Safely evaluate a simple arithmetic expression using ast."""
    try:
        node = ast.parse(expr, mode='eval')
    except Exception:
        return None

    allowed_nodes = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Num, ast.Load,
                     ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.Mod,
                     ast.USub, ast.UAdd, ast.Constant)

    for n in ast.walk(node):
        if not isinstance(n, allowed_nodes):
            return None

    try:
        # ast.literal_eval won't evaluate BinOp, so we compile safely
        code = compile(node, '<string>', 'eval')
        return eval(code, {'__builtins__': {}}, {})
    except Exception:
        return None


def generate_homework_response(user_text):
    """Return (reply_text, suggestion) where suggestion is optional dict with task info.
    Simple local AI responds to common homework prompts and can suggest scheduling slots.
    """
    # Normalize
    txt = (user_text or '').strip()
    lower = txt.lower()

    # Quick math evaluation
    if any(ch.isdigit() for ch in txt) and any(op in txt for op in ['+', '-', '*', '/', '%', '**']):
        val = safe_eval_expr(txt)
        if val is not None:
            return (f"Answer: {val}", None)

    # If user asks to 'explain' or 'summarize' something
    if lower.startswith('explain ') or lower.startswith('what is ') or 'explain' in lower or 'summarize' in lower:
        topic = txt
        reply = (
            f"Study steps for '{topic}':\n"
            "1) Read a short definition or overview.\n"
            "2) Identify key concepts and write them down.\n"
            "3) Do 3–5 practice problems.\n"
            "4) Teach the concept to yourself (out loud) or a friend.\n"
            "5) Create one timed practice session to test recall.\n\n"
            "If you paste a short paragraph I can try to summarize it for you."
        )
        return (reply, None)

    # If user asks to schedule or add a task
    if any(word in lower for word in ['schedule', 'add task', 'add this', 'remind me', 'plan', 'slot']):
        # Try to detect duration like '2h' or '30m'
        import re
        m = re.search(r"(\d+)\s*h", lower)
        minutes = None
        if m:
            minutes = int(m.group(1)) * 60
        else:
            m2 = re.search(r"(\d+)\s*m", lower)
            if m2:
                minutes = int(m2.group(1))

        # Fallback duration
        if minutes is None:
            minutes = 60

        # Use suggest_time_for_task to find a slot
        suggestion = suggest_time_for_task(txt, minutes)
        if suggestion:
            start_dt, end_dt = suggestion
            reply = f"I found a free slot for ~{minutes} minutes: {start_dt.strftime('%m/%d %I:%M %p')} - {end_dt.strftime('%I:%M %p')}.\nWould you like me to add this as a task?"
            suggestion_dict = {"name": txt, "start": start_dt, "end": end_dt, "duration": minutes}
            return (reply, suggestion_dict)
        else:
            return ("I couldn't find a free slot of that length today. Try a shorter duration or another day.", None)

    # Otherwise provide general study tips or fallback
    general = (
        "I can help with: explain <topic>, summarize text, evaluate simple math, or schedule study sessions.\n"
        "Try: 'Explain photosynthesis', 'Summarize <text>', 'Schedule study 2h for calculus'."
    )

    return (general, None)


def open_homework_chat():
    win = tk.Toplevel(root)
    win.title("Homework Chat")
    win.configure(bg=BG_COLOR)
    win.geometry("600x500")

    # Chat history (read-only)
    history = tk.Text(win, wrap=tk.WORD, state=tk.DISABLED, bg=PANEL_BG, fg=ACCENT_COLOR, font=LABEL_FONT)
    history.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10,6))

    # Input area
    input_frame = tk.Frame(win, bg=PANEL_BG)
    input_frame.pack(fill=tk.X, padx=10, pady=(0,10))
    user_entry = ttk.Entry(input_frame)
    user_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,6))

    last_suggestion = {'data': None}

    def append_history(author, text):
        history.config(state=tk.NORMAL)
        history.insert(tk.END, f"{author}: {text}\n\n")
        history.see(tk.END)
        history.config(state=tk.DISABLED)

    def on_send():
        txt = user_entry.get().strip()
        if not txt:
            return
        append_history('You', txt)
        user_entry.delete(0, tk.END)
        # Generate reply in background to keep UI responsive
        def worker():
            reply, suggestion = generate_homework_response(txt)
            last_suggestion['data'] = suggestion
            root.after(0, lambda: append_history('Assistant', reply))
        threading.Thread(target=worker, daemon=True).start()

    def on_add_suggestion_as_task():
        s = last_suggestion.get('data')
        if not s:
            messagebox.showinfo('No Suggestion', 'There is no recent scheduling suggestion to add.')
            return
        # Pre-fill Add Task form and switch to Add page
        show_add_page()
        task_name_entry.delete(0, tk.END)
        task_name_entry.insert(0, s.get('name', 'Homework'))
        start_dt = s.get('start')
        end_dt = s.get('end')
        if start_dt and end_dt:
            start_date_entry.delete(0, tk.END)
            start_date_entry.insert(0, start_dt.strftime('%m%d%Y'))
            start_time_entry.delete(0, tk.END)
            start_time_entry.insert(0, start_dt.strftime('%I:%M'))
            start_am_pm_var.set(start_dt.strftime('%p'))
            end_date_entry.delete(0, tk.END)
            end_date_entry.insert(0, end_dt.strftime('%m%d%Y'))
            end_time_entry.delete(0, tk.END)
            end_time_entry.insert(0, end_dt.strftime('%I:%M'))
            end_am_pm_var.set(end_dt.strftime('%p'))
        messagebox.showinfo('Suggestion Added', 'Suggestion pre-filled in Add Task. Review and click Add Task to save.')

    send_btn = ttk.Button(input_frame, text="Send", command=on_send, style='FlatAccent.TButton')
    send_btn.pack(side=tk.LEFT)

    add_task_btn = ttk.Button(win, text="Add Last Suggestion as Task", command=on_add_suggestion_as_task, style='FlatAccent.TButton')
    add_task_btn.pack(fill=tk.X, padx=10)

    # Enter key binding
    user_entry.bind('<Return>', lambda e: on_send())


def start_brain_break(duration_minutes=5):
    """Open a brain break window with a simple AI-driven mini-game and a countdown.
    After the timer ends, close the window and return to the Add Tasks screen.
    """
    duration_seconds = int(duration_minutes * 60)
    brain_win = tk.Toplevel(root)
    brain_win.title("Brain Break")
    brain_win.configure(bg=BG_COLOR)
    brain_win.geometry("700x420")

    # Layout: left = game, right = timer + controls
    left = tk.Frame(brain_win, bg=PANEL_BG)
    left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(12,6), pady=12)
    right = tk.Frame(brain_win, bg=BG_COLOR, width=200)
    right.pack(side=tk.LEFT, fill=tk.Y, padx=(6,12), pady=12)

    # Game area
    game_title = tk.Label(left, text="Quick Challenge", font=(FONT_FAMILY, 18, "bold"), bg=PANEL_BG, fg=ACCENT_COLOR)
    game_title.pack(pady=(8,6))
    game_text = tk.Label(left, text="", font=(FONT_FAMILY, 14), bg=PANEL_BG, fg=ACCENT_COLOR, wraplength=420, justify='left')
    game_text.pack(pady=(6,12), padx=8)

    answer_var = tk.StringVar()
    answer_entry = ttk.Entry(left, textvariable=answer_var)
    answer_entry.pack(fill=tk.X, padx=10, pady=(0,8))

    feedback = tk.Label(left, text="", font=(FONT_FAMILY, 11), bg=PANEL_BG, fg=ACCENT_COLOR)
    feedback.pack(pady=(4,8))

    controls = tk.Frame(left, bg=PANEL_BG)
    controls.pack(fill=tk.X, padx=10, pady=(4,8))
    submit_btn = ttk.Button(controls, text="Submit", style='FlatAccent.TButton')
    submit_btn.pack(side=tk.LEFT, padx=(0,6))
    skip_btn = ttk.Button(controls, text="Skip", style='Duration.TButton')
    skip_btn.pack(side=tk.LEFT, padx=(6,6))
    end_btn = ttk.Button(controls, text="End Break", style='FlatAccent.TButton')
    end_btn.pack(side=tk.RIGHT)

    # Timer area
    timer_label = tk.Label(right, text="Time Left", font=(FONT_FAMILY, 14, "bold"), bg=BG_COLOR, fg=ACCENT_COLOR)
    timer_label.pack(pady=(24,4))
    countdown_label = tk.Label(right, text="", font=(FONT_FAMILY, 28, "bold"), bg=BG_COLOR, fg=ACCENT_COLOR)
    countdown_label.pack(pady=(4,12))

    hint_label = tk.Label(right, text="Play a quick challenge to refresh your mind.\nWhen time's up you'll be returned to tasks.", font=(FONT_FAMILY, 9), bg=BG_COLOR, fg=ACCENT_COLOR, wraplength=180, justify='left')
    hint_label.pack(padx=8, pady=(6,0))

    # Simple pool of challenges (mix of trivia and math)
    CHALLENGES = [
        ("What is the capital of France?", "paris"),
        ("Unscramble: 'lpaep' (a fruit)", "apple"),
        ("What is 12 * 7?", "84"),
        ("What is the chemical symbol for water?", "h2o"),
        ("Spell the word for the opposite of 'cold' (3 letters).", "hot"),
        ("What is 15 + 28?", "43"),
        ("Unscramble: 'nohtyp' (a programming language)", "python"),
        ("What planet is known as the Red Planet?", "mars")
    ]

    current = {'q': None, 'a': None}

    def pick_challenge():
        q, a = random.choice(CHALLENGES)
        current['q'] = q
        current['a'] = a.lower()
        game_text.config(text=q)
        answer_var.set("")
        feedback.config(text="")
        answer_entry.focus()

    def submit_answer():
        ans = answer_var.get().strip().lower()
        if not ans:
            return
        if ans == current['a']:
            feedback.config(text="Correct! Nice job. 🎉")
        else:
            feedback.config(text=f"Not quite — answer was: {current['a']}")
        # Auto-advance after a short pause
        brain_win.after(1200, pick_challenge)

    def skip_challenge():
        pick_challenge()

    submit_btn.config(command=submit_answer)
    skip_btn.config(command=skip_challenge)

    # Countdown logic using after
    brain_win._remaining = duration_seconds
    brain_win._after_id = None

    def update_countdown():
        mins, secs = divmod(brain_win._remaining, 60)
        countdown_label.config(text=f"{mins:02d}:{secs:02d}")
        # Visual cue when almost done
        if brain_win._remaining <= 10:
            countdown_label.config(fg='#ff6666')
        else:
            countdown_label.config(fg=ACCENT_COLOR)
        if brain_win._remaining <= 0:
            end_break()
            return
        brain_win._remaining -= 1
        brain_win._after_id = brain_win.after(1000, update_countdown)

    def end_break():
        try:
            if brain_win._after_id:
                brain_win.after_cancel(brain_win._after_id)
        except Exception:
            pass
        try:
            brain_win.destroy()
        except Exception:
            pass
        # Return to Add Tasks for studying/tasks
        show_add_page()
        show_success_message("Break over — back to tasks!")
        # Hide break button(s) and restore after 30 minutes
        try:
            disable_break_buttons_for(30)
        except Exception:
            pass

    end_btn.config(command=end_break)

    # Make sure closing the window cancels the after callback
    def on_close():
        try:
            if brain_win._after_id:
                brain_win.after_cancel(brain_win._after_id)
        except Exception:
            pass
        brain_win.destroy()
        # Return to Add Tasks as well
        show_add_page()
        # Hide break button(s) and restore after 30 minutes when user closes the break
        try:
            disable_break_buttons_for(30)
        except Exception:
            pass

    brain_win.protocol("WM_DELETE_WINDOW", on_close)

    # Start
    pick_challenge()
    update_countdown()


### Quiz Pong: AI pong game with questions
QUESTION_POOL = [
    ("What is 7 + 6?", "13"),
    ("What is the capital of Japan?", "tokyo"),
    ("What is 9 * 8?", "72"),
    ("Unscramble: 'nohtyp'", "python"),
    ("What gas do plants breathe in that humans breathe out?", "carbon dioxide"),
    ("What is 100 / 4?", "25"),
    ("Which planet is closest to the Sun?", "mercury"),
    ("What is the square root of 81?", "9"),
    ("Unscramble: 'elppa'", "apple"),
    ("What color do you get when you mix red and white?", "pink")
]

def generate_question_dynamic():
    """Return a (question, answer). Sometimes generate a random math question for variety."""
    if random.random() < 0.45:
        # dynamic math
        a = random.randint(2, 20)
        b = random.randint(2, 20)
        op = random.choice(['+', '-', '*'])
        if op == '+':
            q = f"What is {a} + {b}?"
            ans = str(a + b)
        elif op == '-':
            q = f"What is {a} - {b}?"
            ans = str(a - b)
        else:
            q = f"What is {a} * {b}?"
            ans = str(a * b)
        return (q, ans)
    else:
        q, a = random.choice(QUESTION_POOL)
        return (q, a)


def start_quiz_pong(duration_minutes=5):
    """Start a Pong-style game where the AI is on the right; each player paddle hit spawns a new question."""
    dur_sec = int(duration_minutes * 60)
    w = 700
    h = 420
    game_win = tk.Toplevel(root)
    game_win.title("Quiz Pong")
    game_win.geometry(f"{w}x{h}")
    game_win.configure(bg=BG_COLOR)

    canvas = tk.Canvas(game_win, width=w-220, height=h-40, bg=PANEL_BG, highlightthickness=0)
    canvas.pack(side=tk.LEFT, padx=10, pady=10)

    right_panel = tk.Frame(game_win, bg=BG_COLOR, width=200)
    right_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(6,12), pady=10)

    # Scores and timer
    score_frame = tk.Frame(right_panel, bg=BG_COLOR)
    score_frame.pack(pady=(10,6))
    player_score_var = tk.IntVar(value=0)
    ai_score_var = tk.IntVar(value=0)
    tk.Label(score_frame, text="Player", bg=BG_COLOR, fg=ACCENT_COLOR, font=(FONT_FAMILY,12,'bold')).grid(row=0,column=0,padx=6)
    tk.Label(score_frame, text="AI", bg=BG_COLOR, fg=ACCENT_COLOR, font=(FONT_FAMILY,12,'bold')).grid(row=0,column=1,padx=6)
    tk.Label(score_frame, textvariable=player_score_var, bg=BG_COLOR, fg=ACCENT_COLOR, font=(FONT_FAMILY,18)).grid(row=1,column=0)
    tk.Label(score_frame, textvariable=ai_score_var, bg=BG_COLOR, fg=ACCENT_COLOR, font=(FONT_FAMILY,18)).grid(row=1,column=1)
    # Timer and End Break control
    timer_label = tk.Label(right_panel, text="Time Left", bg=BG_COLOR, fg=ACCENT_COLOR, font=(FONT_FAMILY,12,'bold'))
    timer_label.pack(pady=(12,4))
    countdown_var = tk.StringVar(value="00:00")
    timer_display = tk.Label(right_panel, textvariable=countdown_var, bg=BG_COLOR, fg=ACCENT_COLOR, font=(FONT_FAMILY,20,'bold'))
    timer_display.pack(pady=(0,8))

    # End Break button for the Pong game (same behavior as Trivia)
    end_break_btn = ttk.Button(right_panel, text="End Break", style='FlatAccent.TButton')
    end_break_btn.pack(fill=tk.X, padx=8, pady=(12,6))

    # Game variables
    paddle_w = 10
    paddle_h = 80
    player_x = 10
    ai_x = (w-220) - 10 - paddle_w
    player_y = (h-40)//2 - paddle_h//2
    ai_y = player_y
    ball_r = 8
    ball_x = (w-220)//2
    ball_y = (h-40)//2
    ball_dx = 4 * random.choice([-1,1])
    ball_dy = 3 * random.choice([-1,1])
    ai_speed = 3

    # Draw paddles and ball
    player_paddle = canvas.create_rectangle(player_x, player_y, player_x+paddle_w, player_y+paddle_h, fill=ACCENT_COLOR)
    ai_paddle = canvas.create_rectangle(ai_x, ai_y, ai_x+paddle_w, ai_y+paddle_h, fill=ACCENT_COLOR)
    ball = canvas.create_oval(ball_x-ball_r, ball_y-ball_r, ball_x+ball_r, ball_y+ball_r, fill=ACCENT_COLOR)

    # No quiz questions on the side: this panel only shows timer, scores and End Break
    def set_ai_speed(val):
        nonlocal ai_speed
        try:
            ai_speed = float(val)
        except Exception:
            pass

    # Player controls: move with mouse
    def on_mouse_move(event):
        y = event.y
        # center paddle on cursor
        y0 = max(0, min((h-40)-paddle_h, y - paddle_h//2))
        canvas.coords(player_paddle, player_x, y0, player_x+paddle_w, y0+paddle_h)

    canvas.bind('<Motion>', on_mouse_move)

    # Movement loop
    def game_step():
        nonlocal ball_dx, ball_dy, ball_x, ball_y, ai_y
        # move ball
        ball_x += ball_dx
        ball_y += ball_dy
        # bounce top/bottom
        if ball_y - ball_r <= 0 or ball_y + ball_r >= (h-40):
            ball_dy = -ball_dy
        # paddle collision player
        px0,py0,px1,py1 = canvas.coords(player_paddle)
        ax0,ay0,ax1,ay1 = canvas.coords(ai_paddle)
        if ball_x - ball_r <= px1 and py0 <= ball_y <= py1 and ball_dx < 0:
            ball_dx = -ball_dx
        # paddle collision AI
        if ball_x + ball_r >= ax0 and ay0 <= ball_y <= ay1 and ball_dx > 0:
            ball_dx = -ball_dx
        # score conditions
        if ball_x < 0:
            # AI scores
            ai_score_var.set(ai_score_var.get() + 1)
            reset_ball(direction=1)
        elif ball_x > (w-220):
            # Player scores
            player_score_var.set(player_score_var.get() + 1)
            reset_ball(direction=-1)

        # AI paddle follows ball
        ay_center = (ay0 + ay1)/2
        if ay_center < ball_y - 10:
            new_ay = min((h-40)-paddle_h, ay0 + ai_speed)
        elif ay_center > ball_y + 10:
            new_ay = max(0, ay0 - ai_speed)
        else:
            new_ay = ay0
        canvas.coords(ai_paddle, ai_x, new_ay, ai_x+paddle_w, new_ay+paddle_h)

        # move ball on canvas
        canvas.coords(ball, ball_x-ball_r, ball_y-ball_r, ball_x+ball_r, ball_y+ball_r)
        game_win.after(20, game_step)

    def reset_ball(direction=1):
        nonlocal ball_x, ball_y, ball_dx, ball_dy
        ball_x = (w-220)//2
        ball_y = (h-40)//2
        ball_dx = 4 * direction
        ball_dy = 3 * random.choice([-1,1])
        canvas.coords(ball, ball_x-ball_r, ball_y-ball_r, ball_x+ball_r, ball_y+ball_r)

    # Countdown
    game_win._remaining = dur_sec

    def update_timer():
        mins, secs = divmod(game_win._remaining, 60)
        countdown_var.set(f"{mins:02d}:{secs:02d}")
        if game_win._remaining <= 0:
            end_game()
            return
        game_win._remaining -= 1
        game_win.after(1000, update_timer)

    def end_game():
        try:
            game_win.destroy()
        except Exception:
            pass
        show_add_page()
        show_success_message("Break over — back to tasks!")
        # Hide break button(s) and restore after 30 minutes
        try:
            disable_break_buttons_for(30)
        except Exception:
            pass

    # End Break button wiring (user can end the break early)
    def on_end_break_pressed():
        try:
            # cancel timer and close
            game_win.destroy()
        except Exception:
            pass
        # ensure the same cleanup
        show_add_page()
        show_success_message("Break over — back to tasks!")
        try:
            disable_break_buttons_for(30)
        except Exception:
            pass

    end_break_btn.config(command=on_end_break_pressed)

    # close handler
    def on_close():
        try:
            game_win.destroy()
        except Exception:
            pass
        # When the user closes the Pong window, treat it as ending the break: hide break button(s)
        show_add_page()
        try:
            disable_break_buttons_for(30)
        except Exception:
            pass

    game_win.protocol('WM_DELETE_WINDOW', on_close)

    # initialize
    reset_ball(direction=random.choice([-1,1]))
    game_step()
    update_timer()




def show_ai_panel():
    win = tk.Toplevel(root)
    win.title("AI Assistant")
    win.configure(bg=BG_COLOR)
    win.geometry("400x350")
    win.resizable(True, True)
    tk.Label(win, text="AI Assistant", font=(FONT_FAMILY, 16, "bold"), bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=(10,6))
    tk.Label(win, text="Helpful quick actions to improve your schedule:", bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=(0,8))

    # Create scrollable frame
    canvas = tk.Canvas(win, bg=BG_COLOR, highlightthickness=0)
    scrollbar = tk.Scrollbar(win, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg=BG_COLOR)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Toggle for 5-minute snapping
    enable_snapping_var = tk.BooleanVar(value=enable_5min_snapping)
    check = tk.Checkbutton(scrollable_frame, text="Enable 5-minute snapping", variable=enable_snapping_var, bg=BG_COLOR, fg=ACCENT_COLOR, selectcolor=BG_COLOR, activebackground=BG_COLOR, activeforeground=ACCENT_COLOR, command=lambda: toggle_snapping())
    check.pack(fill=tk.X, padx=20, pady=(6,4))

    def toggle_snapping():
        global enable_5min_snapping
        enable_5min_snapping = enable_snapping_var.get()

    # Pack buttons into scrollable_frame
    ttk.Button(scrollable_frame, text="Auto-categorize tasks", command=auto_categorize_tasks, style='FlatAccent.TButton').pack(fill=tk.X, padx=20, pady=(4,6))
    ttk.Button(scrollable_frame, text="Suggest time for a task", command=suggest_time_for_task_interactive, style='FlatAccent.TButton').pack(fill=tk.X, padx=20, pady=(4,6))
    ttk.Button(scrollable_frame, text="Generate Schedule from Text", command=generate_schedule_from_text, style='FlatAccent.TButton').pack(fill=tk.X, padx=20, pady=(4,6))
    ttk.Button(scrollable_frame, text="Optimize Schedule", command=optimize_schedule, style='FlatAccent.TButton').pack(fill=tk.X, padx=20, pady=(4,6))
    # Homework Chat button
    ttk.Button(win, text="Homework Chat (chat with AI)", command=lambda: open_homework_chat(), style='FlatAccent.TButton').pack(fill=tk.X, padx=20, pady=(6,8))

# AI Assistant quick access on Start screen
ai_btn = ttk.Button(start_btn_frame, text="✨ AI Assistant", command=show_ai_panel, style='FlatAccent.TButton')
ai_btn.pack(fill=tk.X, padx=30, pady=(0, 15), ipady=8)

# Quick access to category manager from start (first button)
edit_categories_btn = ttk.Button(start_btn_frame, text="⚙️ Edit Categories", command=show_category_page, style='FlatAccent.TButton')
edit_categories_btn.pack(fill=tk.X, padx=30, pady=(0, 15), ipady=8)

add_nav_btn = ttk.Button(start_btn_frame, text="📝 Add Tasks", command=show_add_page, style='FlatAccent.TButton')
add_nav_btn.pack(fill=tk.X, padx=30, pady=(0, 15), ipady=8)

overview_nav_btn = ttk.Button(start_btn_frame, text="📊 Overview", command=show_overview_page, style='FlatAccent.TButton')
overview_nav_btn.pack(fill=tk.X, padx=30, pady=(0, 15), ipady=8)

# Unified Break button with chooser (Ping Pong or Trivia)
break_button_enabled = True
break_btn_var = {'widget': None}
# Timestamp for when the next break is allowed again (None = available now)
next_break_available_at = None

def disable_break_buttons_for(duration_minutes=30):
    """Hide the break button(s) for duration_minutes and re-show after timeout."""
    global next_break_available_at
    w = break_btn_var.get('widget')
    # record when the break will be available again
    try:
        next_break_available_at = datetime.now() + timedelta(minutes=duration_minutes)
    except Exception:
        next_break_available_at = None
    if w:
        try:
            w.pack_forget()
        except Exception:
            try:
                w.config(state=tk.DISABLED)
            except Exception:
                pass

    def _restore():
        # Re-pack the button into the start button frame
        try:
            if w:
                w.pack(fill=tk.X, padx=30, pady=(0, 15), ipady=8)
        except Exception:
            pass
        # clear the next-available timestamp
        try:
            nonlocal_next = None
        except Exception:
            pass
        try:
            # set the module-level variable to None
            globals()['next_break_available_at'] = None
        except Exception:
            pass
        show_success_message("Breaks are available again.")

    # Schedule restore on main thread after duration
    try:
        root.after(int(duration_minutes * 60 * 1000), _restore)
    except Exception:
        # Fallback: thread sleep then restore
        def sleeper():
            time.sleep(duration_minutes * 60)
            root.after(0, _restore)
        threading.Thread(target=sleeper, daemon=True).start()

def take_a_break_chooser():
    """Open a small chooser to pick Ping Pong (Quiz Pong) or Trivia (Brain Break)."""
    if not break_button_enabled:
        messagebox.showinfo("Breaks Disabled", "Breaks are temporarily disabled. Try again later.")
        return
    choice = messagebox.askquestion("Take a Break", "Choose your break:\nYes = Ping Pong (Quiz Pong)\nNo = Trivia (Brain Break)")
    # messagebox.askquestion returns 'yes' or 'no'
    if choice == 'yes':
        start_quiz_pong(5)
    else:
        start_brain_break(5)

def update_next_break_label():
    """Update the label on the Start screen to show when the next break will be available."""
    try:
        nb = globals().get('next_break_available_at')
        if nb is None:
            next_break_label.config(text="Next break: Available now")
        else:
            now = datetime.now()
            if nb <= now:
                next_break_label.config(text="Next break: Available now")
                globals()['next_break_available_at'] = None
            else:
                delta = nb - now
                mins, secs = divmod(int(delta.total_seconds()), 60)
                hours, mins = divmod(mins, 60)
                if hours > 0:
                    next_break_label.config(text=f"Next break in: {hours}h {mins}m")
                else:
                    next_break_label.config(text=f"Next break in: {mins}m {secs}s")
    except Exception:
        try:
            next_break_label.config(text="Next break: Unknown")
        except Exception:
            pass
    # schedule again in 1s
    try:
        root.after(1000, update_next_break_label)
    except Exception:
        pass

break_nav_btn = ttk.Button(start_btn_frame, text="🛎️ Take a Break", command=take_a_break_chooser, style='FlatAccent.TButton')
break_nav_btn.pack(fill=tk.X, padx=30, pady=(0, 15), ipady=8)
break_btn_var['widget'] = break_nav_btn

quit_btn = ttk.Button(start_btn_frame, text="❌ Quit", command=root.quit, style='FlatAccent.TButton')
quit_btn.pack(fill=tk.X, padx=30, pady=(0, 15), ipady=8)

# Back button in nav_frame
back_btn = ttk.Button(nav_frame, text="← Back", command=show_start, style='FlatAccent.TButton')

# Initialize
update_category_list()

# Initially hide main UI frames
left_frame.pack_forget()
side_frame.pack_forget()

# Show start screen
show_start()

# Auto-fill current time on startup
set_current_datetime()

# Start background threads
threading.Thread(target=schedule_updater, daemon=True).start()
threading.Thread(target=timer_panel_updater, daemon=True).start()

# Initial updates
canvas.draw()
update_chart()

# Start the next-break countdown updater
try:
    update_next_break_label()
except Exception:
    pass

root.mainloop()
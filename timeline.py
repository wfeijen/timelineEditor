import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Sample task data
tasks = [
    {"Task": "Task A", "Start": datetime.date(2024, 3, 1), "End": datetime.date(2024, 3, 5)},
    {"Task": "Task B", "Start": datetime.date(2024, 3, 4), "End": datetime.date(2024, 3, 10)},
    {"Task": "Task C", "Start": datetime.date(2024, 3, 8), "End": datetime.date(2024, 3, 15)},
    {"Task": "Task d", "Start": datetime.date(2024, 3, 8), "End": datetime.date(2024, 3, 15)},
    {"Task": "Task e", "Start": datetime.date(2024, 3, 8), "End": datetime.date(2024, 3, 15)},
    {"Task": "Task f", "Start": datetime.date(2024, 3, 8), "End": datetime.date(2024, 3, 15)},
    {"Task": "Task g", "Start": datetime.date(2024, 3, 8), "End": datetime.date(2024, 3, 15)},
    {"Task": "Task h", "Start": datetime.date(2024, 3, 8), "End": datetime.date(2024, 3, 15)},
]

selected_task = None  # Track the currently selected task

# Function to update the timeline
def update_timeline():
    ax.clear()  # Clear previous plot

    # Set date formatting
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    ax.set_xlabel("Date")
    ax.set_title("Task Timeline")

    # Generate Y positions so each task has its own row
    y_positions = range(len(tasks), 0, -1)  # Highest task at the top

    # Draw each task on its own horizontal line
    for y, task in zip(y_positions, tasks):
        color = "orange" if task == selected_task else "skyblue"  # Highlight selected task
        ax.barh(y, (task["End"] - task["Start"]).days, 
                left=mdates.date2num(task["Start"]), color=color, label=task["Task"])

    # Adjust Y-axis to show tasks properly
    ax.set_yticks(list(y_positions))
    ax.set_yticklabels([task["Task"] for task in tasks])

    plt.xticks(rotation=45)

    # Prevent layout issues
    fig.tight_layout()

    # Update canvas
    canvas.draw()

# Function to detect clicked task
def on_click(event):
    global selected_task

    if event.inaxes is None:
        return  # Click was outside the graph

    clicked_y = round(event.ydata) if event.ydata else None  # Get closest Y position

    if clicked_y and 1 <= clicked_y <= len(tasks):
        selected_task = tasks[len(tasks) - clicked_y]  # Select task from Y position
        task_name_entry.delete(0, tk.END)
        task_name_entry.insert(0, selected_task["Task"])
        start_date_entry.delete(0, tk.END)
        start_date_entry.insert(0, str(selected_task["Start"]))
        end_date_entry.delete(0, tk.END)
        end_date_entry.insert(0, str(selected_task["End"]))
        update_timeline()

# Function to resize plot on window resize
def resize_plot(event):
    fig.set_size_inches(event.width / 100, event.height / 100)
    update_timeline()

# Function to add a new task
def add_task():
    name = task_name_entry.get()
    start = start_date_entry.get()
    end = end_date_entry.get()
    
    try:
        start_date = datetime.datetime.strptime(start, "%Y-%m-%d").date()
        end_date = datetime.datetime.strptime(end, "%Y-%m-%d").date()
        if start_date >= end_date:
            raise ValueError("Start date must be before End date")
        
        tasks.append({"Task": name, "Start": start_date, "End": end_date})
        update_timeline()
    
    except ValueError as e:
        messagebox.showerror("Invalid Input", str(e))

# Function to delete a task
def delete_task():
    global selected_task
    if not selected_task:
        messagebox.showerror("Error", "No task selected!")
        return

    tasks.remove(selected_task)
    selected_task = None  # Clear selection
    update_timeline()

# Function to edit a task
def edit_task():
    global selected_task
    if not selected_task:
        messagebox.showerror("Error", "No task selected!")
        return

    name = task_name_entry.get()
    start = start_date_entry.get()
    end = end_date_entry.get()
    
    try:
        start_date = datetime.datetime.strptime(start, "%Y-%m-%d").date()
        end_date = datetime.datetime.strptime(end, "%Y-%m-%d").date()
        if start_date >= end_date:
            raise ValueError("Start date must be before End date")

        selected_task["Task"] = name
        selected_task["Start"] = start_date
        selected_task["End"] = end_date
        update_timeline()
    
    except ValueError as e:
        messagebox.showerror("Invalid Input", str(e))

# Tkinter GUI
root = tk.Tk()
root.title("Interactive Timeline Editor")
root.geometry("800x600")

# Make the grid expand with resizing
root.columnconfigure(0, weight=1)
root.rowconfigure(4, weight=1)

# Input Fields
input_frame = tk.Frame(root)
input_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)

tk.Label(input_frame, text="Task Name:").grid(row=0, column=0)
task_name_entry = tk.Entry(input_frame)
task_name_entry.grid(row=0, column=1)

tk.Label(input_frame, text="Start Date (YYYY-MM-DD):").grid(row=1, column=0)
start_date_entry = tk.Entry(input_frame)
start_date_entry.grid(row=1, column=1)

tk.Label(input_frame, text="End Date (YYYY-MM-DD):").grid(row=2, column=0)
end_date_entry = tk.Entry(input_frame)
end_date_entry.grid(row=2, column=1)

# Buttons
btn_frame = tk.Frame(root)
btn_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)

tk.Button(btn_frame, text="Add Task", command=add_task).pack(side="left", padx=5)
tk.Button(btn_frame, text="Edit Task", command=edit_task).pack(side="left", padx=5)
tk.Button(btn_frame, text="Delete Task", command=delete_task).pack(side="left", padx=5)

# Matplotlib Figure (Ensure there's only one canvas here)
fig, ax = plt.subplots(figsize=(8, 4))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas_widget = canvas.get_tk_widget()

# Place the canvas in the root window (only this canvas)
canvas_widget.grid(row=4, column=0, sticky="nsew", padx=10, pady=10)

# Bind events
root.bind("<Configure>", resize_plot)  # Resize event
canvas.mpl_connect("button_press_event", on_click)  # Click event

update_timeline()  # Ensure the initial plot is shown

root.mainloop()
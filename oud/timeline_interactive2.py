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
]

# Function to update the timeline
def update_timeline():
    ax.clear()  # Clear previous plot
    
    # Set date formatting
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    ax.set_xlabel("Date")
    ax.set_ylabel("Tasks")
    ax.set_title("Editable Timeline")
    
    # Draw bars for each task
    for i, task in enumerate(tasks):
        ax.barh(task["Task"], (task["End"] - task["Start"]).days, 
                left=mdates.date2num(task["Start"]), color="skyblue")

    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Update canvas
    canvas.draw()

# Function to update the figure size when window resizes
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
    name = task_name_entry.get()
    global tasks
    tasks = [task for task in tasks if task["Task"] != name]
    update_timeline()

# Function to edit a task
def edit_task():
    name = task_name_entry.get()
    start = start_date_entry.get()
    end = end_date_entry.get()
    
    try:
        start_date = datetime.datetime.strptime(start, "%Y-%m-%d").date()
        end_date = datetime.datetime.strptime(end, "%Y-%m-%d").date()
        if start_date >= end_date:
            raise ValueError("Start date must be before End date")

        for task in tasks:
            if task["Task"] == name:
                task["Start"] = start_date
                task["End"] = end_date
                update_timeline()
                return
        
        messagebox.showerror("Error", "Task not found!")
    
    except ValueError as e:
        messagebox.showerror("Invalid Input", str(e))

# Function to detect clicked task
def on_task_click(event):
    if event.xdata is None or event.ydata is None:
        return  # Clicked outside the graph
    
    # Convert click position to a task index
    y_clicked = int(round(event.ydata))  # Task index approximation

    if 0 <= y_clicked < len(tasks):  
        task = tasks[y_clicked]
        task_name_entry.delete(0, tk.END)
        task_name_entry.insert(0, task["Task"])
        start_date_entry.delete(0, tk.END)
        start_date_entry.insert(0, task["Start"].strftime("%Y-%m-%d"))
        end_date_entry.delete(0, tk.END)
        end_date_entry.insert(0, task["End"].strftime("%Y-%m-%d"))

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

# Matplotlib Figure
fig, ax = plt.subplots(figsize=(8, 4))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas_widget = canvas.get_tk_widget()
canvas_widget.grid(row=4, column=0, sticky="nsew", padx=10, pady=10)

# Bind events
canvas.mpl_connect("button_press_event", on_task_click)  # Detect clicks on bars
root.bind("<Configure>", resize_plot)  # Resize figure when window changes

update_timeline()  # Ensure the initial plot is shown

root.mainloop()
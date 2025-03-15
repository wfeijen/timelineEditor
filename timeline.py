import sys
import datetime
import matplotlib
matplotlib.use('Qt5Agg')  # Ensure the correct backend for PyQt5
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLineEdit, QPushButton, QFormLayout, QHBoxLayout
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.dates as mdates


# Sample task data
tasks = [
    {"Task": "Task A", "Start": datetime.date(2024, 3, 1), "End": datetime.date(2024, 3, 5)},
    {"Task": "Task B", "Start": datetime.date(2024, 3, 4), "End": datetime.date(2024, 3, 10)},
    {"Task": "Task C", "Start": datetime.date(2024, 3, 8), "End": datetime.date(2024, 3, 15)},
    {"Task": "Task D", "Start": datetime.date(2024, 3, 8), "End": datetime.date(2024, 3, 15)},
    {"Task": "Task E", "Start": datetime.date(2024, 3, 8), "End": datetime.date(2024, 3, 15)},
    {"Task": "Task F", "Start": datetime.date(2024, 3, 8), "End": datetime.date(2024, 3, 15)},
]

selected_task = None  # Track the currently selected task


# PyQt Main Window Class
class TaskTimelineEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Interactive Timeline Editor")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout(self.central_widget)

        # Initialize the FigureCanvas without the self argument
        self.figure = plt.Figure(figsize=(8, 4))
        self.canvas = FigureCanvas(self.figure)  # Corrected the initialization
        layout.addWidget(self.canvas)

        # Layout for task name, start date, and end date inputs
        self.form_layout = QFormLayout()
        self.task_name_entry = QLineEdit(self)
        self.start_date_entry = QLineEdit(self)
        self.end_date_entry = QLineEdit(self)
        self.form_layout.addRow("Task Name", self.task_name_entry)
        self.form_layout.addRow("Start Date (YYYY-MM-DD)", self.start_date_entry)
        self.form_layout.addRow("End Date (YYYY-MM-DD)", self.end_date_entry)
        layout.addLayout(self.form_layout)

        # Buttons
        self.buttons_layout = QHBoxLayout()
        self.add_task_button = QPushButton("Add Task", self)
        self.edit_task_button = QPushButton("Edit Task", self)
        self.delete_task_button = QPushButton("Delete Task", self)

        self.buttons_layout.addWidget(self.add_task_button)
        self.buttons_layout.addWidget(self.edit_task_button)
        self.buttons_layout.addWidget(self.delete_task_button)

        layout.addLayout(self.buttons_layout)

        # Connect button actions
        self.add_task_button.clicked.connect(self.add_task)
        self.edit_task_button.clicked.connect(self.edit_task)
        self.delete_task_button.clicked.connect(self.delete_task)

        self.selected_task = None  # Initially, no task is selected

        self.update_timeline()  # Initial drawing of the timeline

        # Connect the canvas click event to the task selection
        self.canvas.mpl_connect('button_press_event', self.on_canvas_click)

    def update_timeline(self):
        # Clear the canvas
        self.figure.clf()

        # Matplotlib part for plotting the timeline
        ax = self.figure.add_subplot(111)

        # Set date formatting
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        ax.set_xlabel("Date")
        ax.set_title("Task Timeline")

        # Generate Y positions so each task has its own row
        y_positions = range(len(tasks), 0, -1)  # Highest task at the top

        # Draw each task on its own horizontal line
        self.rectangles = []  # List to store all rectangle objects (bars)
        for y, task in zip(y_positions, tasks):
            color = "orange" if task == self.selected_task else "skyblue"  # Highlight selected task
            bar_container = ax.barh(y, (task["End"] - task["Start"]).days,
                                    left=mdates.date2num(task["Start"]), color=color)
            for rect in bar_container:  # Extract each rectangle from the BarContainer
                rect.set_label(task["Task"])  # Store the task name in the label
                self.rectangles.append((rect, task))  # Store the task with the corresponding rectangle

        # Adjust Y-axis to show tasks properly
        ax.set_yticks(list(y_positions))
        ax.set_yticklabels([task["Task"] for task in tasks])

        plt.xticks(rotation=45)

        # Prevent layout issues
        self.figure.tight_layout()

        # Update canvas
        self.canvas.draw()

    def add_task(self):
        name = self.task_name_entry.text()
        start = self.start_date_entry.text()
        end = self.end_date_entry.text()

        try:
            start_date = datetime.datetime.strptime(start, "%Y-%m-%d").date()
            end_date = datetime.datetime.strptime(end, "%Y-%m-%d").date()

            if start_date >= end_date:
                raise ValueError("Start date must be before End date")

            tasks.append({"Task": name, "Start": start_date, "End": end_date})
            self.update_timeline()

        except ValueError as e:
            print(f"Error: {e}")

    def edit_task(self):
        if not self.selected_task:
            print("No task selected!")
            return

        name = self.task_name_entry.text()
        start = self.start_date_entry.text()
        end = self.end_date_entry.text()

        try:
            start_date = datetime.datetime.strptime(start, "%Y-%m-%d").date()
            end_date = datetime.datetime.strptime(end, "%Y-%m-%d").date()

            if start_date >= end_date:
                raise ValueError("Start date must be before End date")

            self.selected_task["Task"] = name
            self.selected_task["Start"] = start_date
            self.selected_task["End"] = end_date
            self.update_timeline()

        except ValueError as e:
            print(f"Error: {e}")

    def delete_task(self):
        if not self.selected_task:
            print("No task selected!")
            return

        tasks.remove(self.selected_task)
        self.selected_task = None  # Clear selection
        self.update_timeline()

    def on_canvas_click(self, event):
        # Check for click in each rectangle (task bar)
        for rect, task in self.rectangles:
            if rect.contains(event)[0]:  # Check if click is within the rectangle
                self.selected_task = task
                print(f"Selected task: {self.selected_task['Task']}")
                self.update_timeline()  # Re-render the timeline with the selected task highlighted
                break  # Stop further checking after finding the clicked task


# PyQt Application
def main():
    app = QApplication(sys.argv)
    window = TaskTimelineEditor()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
import sys
import datetime
import matplotlib
matplotlib.use('Qt5Agg')  # Ensure the correct backend for PyQt5
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLineEdit, QPushButton, QFormLayout, QHBoxLayout, QPlainTextEdit
# from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.dates as mdates
from Directory_handler import Directory_handler


# PyQt Main Window Class
class chapterTimelineEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        # load Data from dir ["chapter", "path", "plot", "synopsis", "startdate", "enddate"]
        self.directory_handler = Directory_handler("/home/willem/Documents/Eigen maaksels/Verhalen staan buiten bin en in dropbox/radio controlled/content")
        self.chapterlist = self.directory_handler.get_metadata()
        self.selected_chapter = None  # Track the currently selected chapter

        self.setWindowTitle("Interactive Timeline Editor")
        self.setGeometry(0, 0, 1800, 1600)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout(self.central_widget)

        # Initialize the FigureCanvas without the self argument
        self.figure = plt.Figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)  # Corrected the initialization
        layout.addWidget(self.canvas)

        # Layout for chapter name, startdate date, enddate date, and plot (project) inputs
        self.form_layout = QFormLayout()
        self.chapter_name_entry = QLineEdit(self)
        self.startdate_date_entry = QLineEdit(self)
        self.enddate_date_entry = QLineEdit(self)
        self.plot_name_entry = QLineEdit(self)  # plot (project) name input
        self.synopsis_name_entry = QPlainTextEdit(self)
        self.form_layout.addRow("chapter Name", self.chapter_name_entry)
        self.form_layout.addRow("startdate Date (YYYY-MM-DD)", self.startdate_date_entry)
        self.form_layout.addRow("enddate Date (YYYY-MM-DD)", self.enddate_date_entry)
        self.form_layout.addRow("plot", self.plot_name_entry)  # plot name entry
        self.form_layout.addRow("synopsis", self.synopsis_name_entry)  # plot name entry
        layout.addLayout(self.form_layout)

        # Buttons
        self.buttons_layout = QHBoxLayout()
        self.update_chapter_button = QPushButton("Update chapter", self)
        self.save_timelines_button = QPushButton("Save timelines", self)
     
        self.buttons_layout.addWidget(self.update_chapter_button)
        self.buttons_layout.addWidget(self.save_timelines_button)
    
        layout.addLayout(self.buttons_layout)

        # Connect button actions
        self.update_chapter_button.clicked.connect(self.update_chapter)
        self.save_timelines_button.clicked.connect(self.save_timelines)
    
        self.selected_chapter = None  # Initially, no chapter is selected

        self.update_timeline()  # Initial drawing of the timeline

        # Connect the canvas resize event to dynamically scale the labels
        self.canvas.mpl_connect('resize_event', self.on_resize)

        # Connect the canvas click event to the chapter selection
        self.canvas.mpl_connect('button_press_event', self.on_canvas_click)

    def update_timeline(self):
        # Clear the canvas
        self.figure.clf()

        # Matplotlib part for plotting the timeline
        ax = self.figure.add_subplot(111)

        # Set date formatting
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        ax.set_xlabel("Date", fontsize = 20)
        ax.set_title("chapter Timeline", fontsize = 20)

        # Group chapters by plot
        plot_groups = {}
        for chapter in self.chapterlist:
            if chapter["plot"] not in plot_groups:
                plot_groups[chapter["plot"]] = []
            plot_groups[chapter["plot"]].append(chapter)

        # Generate Y positions based on plot (each plot corresponds to a project)
        plot_labels = list(plot_groups.keys())
        y_positions = {plot: idx + 1 for idx, plot in enumerate(plot_labels)}  # Assign Y positions to plots

        # Draw each chapter on its respective plot
        self.rectangles = []  # List to store all rectangle objects (bars)
        for chapter in self.chapterlist:
            color = "orange" if chapter == self.selected_chapter else "skyblue"  # Highlight selected chapter
            plot_position = y_positions[chapter["plot"]]  # Get Y position for the chapter's plot
            bar_container = ax.barh(plot_position, (chapter["enddate"] - chapter["startdate"]).days,
                                    left=mdates.date2num(chapter["startdate"]), color=color)
            for rect in bar_container:  # Extract each rectangle from the BarContainer
                rect.set_label(chapter["chapter"])  # Store the chapter name in the label
                self.rectangles.append((rect, chapter))  # Store the chapter with the corresponding rectangle

                # Add chapter name to the center of the bar
                ax.text(
                    mdates.date2num(chapter["startdate"]) + (chapter["enddate"] - chapter["startdate"]).days / 2,
                    plot_position,
                    chapter["chapter"],
                    ha="center", va="center", color="black", fontsize = 20)

        # Adjust Y-axis to show names
        ax.set_yticks(range(1, len(plot_labels) + 1))
        ax.set_yticklabels(plot_labels, fontsize = 20)

        # Scale the X-ticks (dates) with the window size
        ax.tick_params(axis='x', labelsize=20)

        # Prevent layout issues
        self.figure.tight_layout()

        # Update canvas
        self.canvas.draw()

    def get_scaled_font_size(self):
        # Scale font size based on figure size
        width, height = self.figure.get_size_inches()
        scale_factor = width / 8  # Scale factor based on figure width (you can adjust this factor)
        return max(10, int(scale_factor))  # Minimum font size of 10

    def update_chapter(self):
        if not self.selected_chapter:
            print("No chapter selected!")
            return

        name = self.chapter_name_entry.text()
        startdate = self.startdate_date_entry.text()
        enddate = self.enddate_date_entry.text()
        plot = self.plot_name_entry.text()
        synopsis = self.synopsis_name_entry.toPlainText() 

        try:
            startdate_date = datetime.datetime.strptime(startdate, "%Y-%m-%d").date()
            enddate_date = datetime.datetime.strptime(enddate, "%Y-%m-%d").date()

            if startdate_date >= enddate_date:
                raise ValueError("startdate date must be before enddate date")

            self.selected_chapter["chapter"] = name
            self.selected_chapter["startdate"] = startdate_date
            self.selected_chapter["enddate"] = enddate_date
            self.selected_chapter["plot"] = plot  # Update the plot name
            self.selected_chapter["synopsis"] = synopsis  # Update the plot name
            self.update_timeline()

        except ValueError as e:
            print(f"Error: {e}")
    
    def save_timelines(self):
        self.directory_handler.set_metadata(self.chapterlist)

    def on_resize(self, event):
        # Update the font size when resizing
        self.update_timeline()

    def on_canvas_click(self, event):
        # Check for click in each rectangle (chapter bar)
        for rect, chapter in self.rectangles:
            if rect.contains(event)[0]:  # Check if click is within the rectangle
                self.selected_chapter = chapter
                print(f"Selected chapter: {self.selected_chapter['chapter']}")

                # Populate the text boxes with the selected chapter information
                self.chapter_name_entry.setText(self.selected_chapter["chapter"])
                self.startdate_date_entry.setText(self.selected_chapter["startdate"].strftime("%Y-%m-%d"))
                self.enddate_date_entry.setText(self.selected_chapter["enddate"].strftime("%Y-%m-%d"))
                self.plot_name_entry.setText(self.selected_chapter["plot"])  # Show the plot name (project)
                self.synopsis_name_entry.setPlainText(self.selected_chapter["synopsis"])

                self.update_timeline()  # Re-renddateer the timeline with the selected chapter highlighted
                break  # Stop further checking after finding the clicked chapter


# PyQt Application
def main():
    app = QApplication(sys.argv)
    window = chapterTimelineEditor()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

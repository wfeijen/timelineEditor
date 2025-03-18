import sys
import datetime
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLineEdit, QPushButton, QFormLayout, QHBoxLayout, QPlainTextEdit, QLabel, QSlider, QDateEdit
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from Directory_handler import Directory_handler
matplotlib.use('Qt5Agg')  # Ensure the correct backend for PyQt5


# PyQt Main Window Class
class chapterTimelineEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        # load Data from dir ["chapter", "path", "plot", "synopsis", "startdate", "enddate"]
        self.directory_handler = Directory_handler("/home/willem/Documents/Eigen maaksels/Verhalen staan buiten bin en in dropbox/radio controlled/content")
        self.chapterlist = self.directory_handler.get_metadata()
        self.selected_chapter = None  # Track the currently selected chapter

        self.setWindowTitle("Interactive Timeline Editor")
        self.setGeometry(0, 0, 1920, 1600)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout(self.central_widget)

        # Initialize the FigureCanvas without the self argument
        self.figure = plt.Figure(figsize=(1, 20))
        self.canvas = FigureCanvas(self.figure)  # Corrected the initialization
        layout.addWidget(self.canvas)

        # Layout for chapter name, startdate date, duur, and plot (project) inputs
        self.form_layout = QFormLayout()
        self.chapter_name_entry = QLineEdit(self)
        self.startdate_date_entry = QDateEdit(calendarPopup=True)
        self.startdate_date_entry.setDisplayFormat("yyyy-MM-dd")
        self.duur_entry = QLineEdit(self)
        self.plot_name_entry = QLineEdit(self)
        self.pov_name_entry = QLineEdit(self)
        self.char_name_entry = QLineEdit(self)
        self.synopsis_name_entry = QPlainTextEdit(self)
        self.form_layout.addRow("chapter Name", self.chapter_name_entry)
        self.form_layout.addRow("startdate Date (YYYY-MM-DD)", self.startdate_date_entry)
        self.form_layout.addRow("duur ", self.duur_entry)
        self.form_layout.addRow("plot", self.plot_name_entry)
        self.form_layout.addRow("pov", self.pov_name_entry)
        self.form_layout.addRow("char", self.char_name_entry)
        self.form_layout.addRow("synopsis", self.synopsis_name_entry)
        layout.addLayout(self.form_layout)
     

        # Buttons
        self.buttons_layout = QHBoxLayout()
        self.update_chapter_button = QPushButton("Update chapter", self)
        self.save_timelines_button = QPushButton("Save timelines", self)
        self.reload_timelines_button = QPushButton("Reload timelines", self)
     
        self.buttons_layout.addWidget(self.update_chapter_button)
        self.buttons_layout.addWidget(self.save_timelines_button)
        self.buttons_layout.addWidget(self.reload_timelines_button)
    
        layout.addLayout(self.buttons_layout)

        # Connect button actions
        self.update_chapter_button.clicked.connect(self.update_chapter)
        self.save_timelines_button.clicked.connect(self.save_timelines)
        self.reload_timelines_button.clicked.connect(self.reload_timelines)

        # Add sliders for filtering by start and end dates
        self.start_slider_label = QLabel("Start: N/A", self)
        self.start_slider = QSlider(Qt.Horizontal)
        self.start_slider.setTickInterval(1)
        self.start_slider.setSingleStep(1)
        layout.addWidget(self.start_slider_label)
        layout.addWidget(self.start_slider)

        self.end_slider_label = QLabel("End: N/A", self)
        self.end_slider = QSlider(Qt.Horizontal)
        self.end_slider.setTickInterval(1)
        self.end_slider.setSingleStep(1)
        layout.addWidget(self.end_slider_label)
        layout.addWidget(self.end_slider)

        # Set slider limits
        self.setup_sliders()

        # Connect slider events
        self.start_slider.valueChanged.connect(self.update_slider_labels)
        self.end_slider.valueChanged.connect(self.update_slider_labels)
    
        self.selected_chapter = None  # Initially, no chapter is selected

        self.update_timeline()  # Initial drawing of the timeline

        # Connect the canvas resize event to dynamically scale the labels
        self.canvas.mpl_connect('resize_event', self.on_resize)

        # Connect the canvas click event to the chapter selection
        self.canvas.mpl_connect('button_press_event', self.on_canvas_click)
        
    
    def setup_sliders(self):
        """Initialize sliders based on data range."""
        if not self.chapterlist:
            return

        min_date = min(ch["startdate"] for ch in self.chapterlist)
        max_date = max(ch["enddate"] for ch in self.chapterlist)

        # Convert dates to numerical format for sliders
        min_num = mdates.date2num(min_date)
        max_num = mdates.date2num(max_date)

        self.start_slider.setMinimum(int(min_num))
        self.start_slider.setMaximum(int(max_num))
        self.start_slider.setValue(int(min_num))

        self.end_slider.setMinimum(int(min_num))
        self.end_slider.setMaximum(int(max_num))
        self.end_slider.setValue(int(max_num))

        self.update_slider_labels()

    def update_slider_labels(self):
        start_filter = mdates.num2date(self.start_slider.value()).replace(tzinfo=None)
        end_filter = mdates.num2date(self.end_slider.value()).replace(tzinfo=None)

        if start_filter > end_filter:
            return  

        self.start_slider_label.setText(f"Start: {start_filter.strftime('%Y-%m-%d')}")
        self.end_slider_label.setText(f"End: {end_filter.strftime('%Y-%m-%d')}")

        self.update_timeline()

    def update_timeline(self):
        # Clear the canvas
        self.figure.clf()
        scaledFontSize = self.get_scaled_font_size()
        vertical_positions = ['top', 'bottom', 'center']

        # Matplotlib part for plotting the timeline
        ax = self.figure.add_subplot(111)

        start_filter = mdates.num2date(self.start_slider.value()).date()
        end_filter = mdates.num2date(self.end_slider.value()).date()

        filtered_chapters = [
            ch for ch in self.chapterlist 
            if ch["startdate"] >= start_filter and ch["enddate"] <= end_filter
        ]

        # Set date formatting
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        ax.set_xlabel("Date", fontsize = scaledFontSize)
        ax.set_title("chapter Timeline", fontsize = scaledFontSize)

        # Group chapters by plot
        plot_groups = {}
        for chapter in filtered_chapters:
            plot_list = chapter["plot"].split(",")
            for p in plot_list:
                plot = p.strip()
                if plot not in plot_groups:
                    plot_groups[plot] = []
                plot_groups[plot].append(chapter)

        
        # Generate Y positions based on plot (each plot corresponds to a project)
        plot_labels = sorted(list(plot_groups.keys()), reverse=True)
        y_positions = {plot: idx + 1 for idx, plot in enumerate(plot_labels)}  # Assign Y positions to plots

        # Draw each chapter on its respective plot
        self.rectangles = []  # List to store all rectangle objects (bars)
        j = 0
        for chapter in filtered_chapters:
            color = "orange" if chapter == self.selected_chapter else "skyblue"  # Highlight selected chapter
            plot_list = chapter["plot"].split(",")
            for p in plot_list:
                plot = p.strip()
                plot_position = y_positions[plot]  # Get Y position for the chapter's plot
                bar_container = ax.barh(plot_position, (chapter["enddate"] - chapter["startdate"]).days,
                                        left=mdates.date2num(chapter["startdate"]), color=color)
                for rect in bar_container:  # Extract each rectangle from the BarContainer
                    rect.set_label(chapter["chapter"])  # Store the chapter name in the label
                    self.rectangles.append((rect, chapter))  # Store the chapter with the corresponding rectangle

                    # Add chapter name to the center of the bar
                    va = vertical_positions[j ]
                    j = (j + 1)% 3
                    ax.text(
                        mdates.date2num(chapter["startdate"]) + (chapter["enddate"] - chapter["startdate"]).days / 2,
                        plot_position + (j/3) -(1/3),
                        chapter["chapter"],
                        ha="center", va='center', color="black", fontsize = scaledFontSize)

        # Adjust Y-axis to show names
        ax.set_yticks(range(1, len(plot_labels) + 1))
        ax.set_yticklabels(plot_labels, fontsize = scaledFontSize)

        # Scale the X-ticks (dates) with the window size
        ax.tick_params(axis='x', labelsize=scaledFontSize)

        # Prevent layout issues
        self.figure.tight_layout()

        # Update canvas
        self.canvas.draw()

    def get_scaled_font_size(self):
        # Scale font size based on figure size
        width, height = self.figure.get_size_inches()
        scale_factor = height / 8  # Scale factor based on figure width (you can adjust this factor)
        return max(20, int(scale_factor))  # Minimum font size of 10

    def update_chapter(self):
        if not self.selected_chapter:
            print("No chapter selected!")
            return

        name = self.chapter_name_entry.text()
        startdate_datetime = self.startdate_date_entry.date().toPyDate()
        duur = self.duur_entry.text()
        plot = self.plot_name_entry.text()
        pov = self.pov_name_entry.text()
        char = self.char_name_entry.text()
        synopsis = self.synopsis_name_entry.toPlainText() 

        try:
            duur = int(duur)
        except ValueError as e:
            duur = 1

        try:
            enddate_datetime = startdate_datetime + datetime.timedelta(days=duur)
        except ValueError as e:
            print(f"Error: {e}")   
       
        try:
            self.selected_chapter["chapter"] = name
            self.selected_chapter["startdate"] = startdate_datetime
            self.selected_chapter["enddate"] = enddate_datetime
            self.selected_chapter["plot"] = plot
            self.selected_chapter["pov"] = pov
            self.selected_chapter["char"] = char
            self.selected_chapter["synopsis"] = synopsis

            if mdates.date2num(startdate_datetime) < self.start_slider.minimum() or mdates.date2num(enddate_datetime) > self.end_slider.maximum():
                self.setup_sliders()
            self.update_timeline()

        except ValueError as e:
            print(f"Error: {e}")
    
    def save_timelines(self):
        self.directory_handler.set_metadata(self.chapterlist)

    def reload_timelines(self):
        self.chapterlist = self.directory_handler.get_metadata()
        self.selected_chapter = None  # Track the currently selected chapter
        self.update_timeline()

    def on_resize(self, event):
        # Update the font size when resizing
        self.update_timeline()

    def on_canvas_click(self, event):
        # Check for click in each rectangle (chapter bar)

        for rect, chapter in self.rectangles:
            if rect.contains(event)[0]:  # Check if click is within the rectangle
                self.update_chapter()
                try:# Tijdelijk verwijderen signal om problemen te voorkomen
                    self.startdate_date_entry.dateTimeChanged.disconnect()
                    self.duur_entry.textChanged.disconnect()
                except Exception: pass

                self.selected_chapter = chapter
                print(f"Selected chapter: {self.selected_chapter['chapter']}")

                # Populate the text boxes with the selected chapter information
                self.chapter_name_entry.setText(self.selected_chapter["chapter"])
                self.startdate_date_entry.setDate(self.selected_chapter["startdate"])
                self.duur_entry.setText(str((self.selected_chapter["enddate"]-self.selected_chapter["startdate"]).days))
                self.plot_name_entry.setText(self.selected_chapter["plot"])
                self.pov_name_entry.setText(self.selected_chapter["pov"])
                self.char_name_entry.setText(self.selected_chapter["char"])
                self.synopsis_name_entry.setPlainText(self.selected_chapter["synopsis"])

                # Bijwerken na verandering via signal
                self.startdate_date_entry.dateTimeChanged.connect(lambda: self.update_chapter()) 
                self.duur_entry.textChanged.connect(self.update_chapter)


                self.update_timeline()  # Re-renddateer the timeline with the selected chapter highlighted
                break  # Stop further checking after finding the clicked chapter

                # Connect update event to edit fields



# PyQt Application
def main():
    app = QApplication(sys.argv)
    window = chapterTimelineEditor()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

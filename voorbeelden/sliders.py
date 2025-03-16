import sys
import datetime
import matplotlib
matplotlib.use('Qt5Agg')  # Ensure the correct backend for PyQt5
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLineEdit, QPushButton, 
    QFormLayout, QHBoxLayout, QPlainTextEdit, QLabel, QSlider
)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.dates as mdates
from Directory_handler import Directory_handler

class ChapterTimelineEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        # Load Data from directory
        self.directory_handler = Directory_handler(
            "/home/willem/Documents/Eigen maaksels/Verhalen staan buiten bin en in dropbox/radio controlled/content"
        )
        self.chapterlist = self.directory_handler.get_metadata()
        self.selected_chapter = None  

        self.setWindowTitle("Interactive Timeline Editor")
        self.setGeometry(0, 0, 1800, 1600)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout(self.central_widget)

        # Initialize the FigureCanvas
        self.figure = plt.Figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Form layout for input fields
        self.form_layout = QFormLayout()
        self.chapter_name_entry = QLineEdit(self)
        self.startdate_date_entry = QLineEdit(self)
        self.enddate_date_entry = QLineEdit(self)
        self.plot_name_entry = QLineEdit(self)
        self.synopsis_name_entry = QPlainTextEdit(self)

        self.form_layout.addRow("Chapter Name", self.chapter_name_entry)
        self.form_layout.addRow("Start Date (YYYY-MM-DD)", self.startdate_date_entry)
        self.form_layout.addRow("End Date (YYYY-MM-DD)", self.enddate_date_entry)
        self.form_layout.addRow("Plot", self.plot_name_entry)
        self.form_layout.addRow("Synopsis", self.synopsis_name_entry)
        layout.addLayout(self.form_layout)

        # Buttons
        self.buttons_layout = QHBoxLayout()
        self.update_chapter_button = QPushButton("Update Chapter", self)
        self.save_timelines_button = QPushButton("Save Timelines", self)

        self.buttons_layout.addWidget(self.update_chapter_button)
        self.buttons_layout.addWidget(self.save_timelines_button)
        layout.addLayout(self.buttons_layout)

        # Connect button actions
        self.update_chapter_button.clicked.connect(self.update_chapter)
        self.save_timelines_button.clicked.connect(self.save_timelines)

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

        self.selected_chapter = None  

        self.update_timeline()  # Initial drawing of the timeline

        # Connect canvas events
        self.canvas.mpl_connect('resize_event', self.on_resize)
        self.canvas.mpl_connect('button_press_event', self.on_canvas_click)

    def on_resize(self, event):
        self.update_timeline()

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
        """Update slider labels and redraw the timeline based on selected range."""
        start_filter = mdates.num2date(self.start_slider.value()).replace(tzinfo=None)
        end_filter = mdates.num2date(self.end_slider.value()).replace(tzinfo=None)

        if start_filter > end_filter:
            return  

        self.start_slider_label.setText(f"Start: {start_filter.strftime('%Y-%m-%d')}")
        self.end_slider_label.setText(f"End: {end_filter.strftime('%Y-%m-%d')}")

        self.update_timeline()

    def update_timeline(self):
        """Redraw the timeline within the selected date range."""
        self.figure.clf()
        ax = self.figure.add_subplot(111)

        start_filter = mdates.num2date(self.start_slider.value()).replace(tzinfo=None)
        end_filter = mdates.num2date(self.end_slider.value()).replace(tzinfo=None)

        filtered_chapters = [
            ch for ch in self.chapterlist 
            if ch["startdate"] >= start_filter and ch["enddate"] <= end_filter
        ]

        plot_groups = {}
        for chapter in filtered_chapters:
            if chapter["plot"] not in plot_groups:
                plot_groups[chapter["plot"]] = []
            plot_groups[chapter["plot"]].append(chapter)

        plot_labels = list(plot_groups.keys())
        y_positions = {plot: idx + 1 for idx, plot in enumerate(plot_labels)}

        self.rectangles = []
        for chapter in filtered_chapters:
            color = "orange" if chapter == self.selected_chapter else "skyblue"
            plot_position = y_positions[chapter["plot"]]
            bar_container = ax.barh(plot_position, (chapter["enddate"] - chapter["startdate"]).days,
                                    left=mdates.date2num(chapter["startdate"]), color=color)
            for rect in bar_container:
                rect.set_label(chapter["chapter"])
                self.rectangles.append((rect, chapter))

                ax.text(
                    mdates.date2num(chapter["startdate"]) + (chapter["enddate"] - chapter["startdate"]).days / 2,
                    plot_position,
                    chapter["chapter"],
                    ha="center", va="center", color="black", fontsize=12
                )

        ax.set_yticks(range(1, len(plot_labels) + 1))
        ax.set_yticklabels(plot_labels, fontsize=12)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        ax.tick_params(axis='x', labelsize=12)

        self.figure.tight_layout()
        self.canvas.draw()

    def update_chapter(self):
        if not self.selected_chapter:
            return

        name = self.chapter_name_entry.text()
        startdate = self.startdate_date_entry.text()
        enddate = self.enddate_date_entry.text()
        plot = self.plot_name_entry.text()
        synopsis = self.synopsis_name_entry.toPlainText()

        try:
            startdate_date = datetime.datetime.strptime(startdate, "%Y-%m-%d").date()
            enddate_date = datetime.datetime.strptime(enddate, "%Y-%m-%d").date()

            self.selected_chapter.update({
                "chapter": name, "startdate": startdate_date,
                "enddate": enddate_date, "plot": plot, "synopsis": synopsis
            })

            self.update_timeline()
        except ValueError as e:
            print(f"Error: {e}")

    def save_timelines(self):
        self.directory_handler.set_metadata(self.chapterlist)

    def on_canvas_click(self, event):
        pass  # (Omitted for brevity)

def main():
    app = QApplication(sys.argv)
    window = ChapterTimelineEditor()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
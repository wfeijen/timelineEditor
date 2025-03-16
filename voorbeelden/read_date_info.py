import os
import pandas as pd
from datetime import datetime, timedelta

def extract_metadata(file_path):
    metadata = {"name": None, "path": None, "plot": "geen_plot", "startdate": None, "enddate": None}
    time_values = []
    
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            if line.startswith("%%~name:"):
                metadata["name"] = line.split("%%~name:")[1].strip()
            elif line.startswith("%%~path: 38afc2dd349ba/"):
                metadata["path"] = line.split("%%~path: 38afc2dd349ba/")[1].strip()
            elif line.startswith("@plot:"):
                plot_value = line.split("@plot:")[1].strip()
                if plot_value:
                    metadata["plot"] = plot_value
            elif line.startswith("@time:"):
                time_value = line.split("@time:")[1].strip()
                try:
                    time_values.append(datetime.strptime(time_value, "%Y-%m-%d"))
                except ValueError:
                    continue
    
    if time_values:
        metadata["startdate"] = min(time_values).strftime("%Y-%m-%d")
        metadata["enddate"] = max(time_values).strftime("%Y-%m-%d") if len(time_values) > 1 else (time_values[0] + timedelta(days=1)).strftime("%Y-%m-%d")
    else:
        return None
    
    return metadata

def process_nwd_files(directory):
    data = []
    
    for filename in os.listdir(directory):
        if filename.endswith(".nwd"):
            file_path = os.path.join(directory, filename)
            metadata = extract_metadata(file_path)
            if metadata:
                data.append(metadata)
    
    return pd.DataFrame(data, columns=["name", "path", "plot", "startdate", "enddate"])

# Set your directory path
directory_path = "/home/willem/Documents/Eigen maaksels/Verhalen staan buiten bin en in dropbox/radio controlled/content"

df = process_nwd_files(directory_path)
print(df)

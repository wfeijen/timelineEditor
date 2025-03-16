import os
import pandas as pd
from datetime import datetime, timedelta

def extract_metadata(file_path):
    metadata = {"name": None, "path": None, "plot": "geen_plot", "startdate": None, "enddate": None, "lines": []}
    time_values = []
    
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            metadata["lines"].append(line)
            if line.startswith("%%~name:"):
                metadata["name"] = line.split("%%~name:")[1].strip()
            elif line.startswith("%%~path:"):
                metadata["path"] = line.split("%%~path:")[1].strip()
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
        metadata["startdate"] = min(time_values)
        metadata["enddate"] = max(time_values) if len(time_values) > 1 else (time_values[0] + timedelta(days=1))
    else:
        return None
    
    return metadata

def process_nwd_files(directory):
    data = []
    metadata_dict = {}
    
    for filename in os.listdir(directory):
        if filename.endswith(".nwd"):
            file_path = os.path.join(directory, filename)
            metadata = extract_metadata(file_path)
            if metadata:
                # Add a day to the enddate
                metadata["enddate"] = (metadata["enddate"] + timedelta(days=1))
                data.append(metadata)
                metadata_dict[metadata["path"]] = metadata
    
    df = pd.DataFrame(data, columns=["name", "path", "plot", "startdate", "enddate"])
    return df, metadata_dict

def update_nwd_files(directory, df, metadata_dict):
    for _, row in df.iterrows():
        file_path = None
        for filename in os.listdir(directory):
            full_path = os.path.join(directory, filename)
            if filename.endswith(".nwd") and metadata_dict.get(row["path"], {}).get("path") == row["path"]:
                file_path = full_path
                break
        
        if file_path:
            with open(file_path, "r", encoding="utf-8") as file:
                lines = file.readlines()
            
            # Remove existing @plot: and @time:
            lines = [line for line in lines if not line.startswith("@plot:") and not line.startswith("@time:")]
            
            # Add new metadata after %%~date:
            new_metadata = [
                f"@plot: {row['plot']}\n",
                f"@time: {row['startdate']}\n",
                f"@time: {row['enddate']}\n"
            ]
            
            updated_lines = new_metadata + lines
            
            with open(file_path, "w", encoding="utf-8") as file:
                file.writelines(updated_lines)

# Set your directory path
directory_path = "/home/willem/Documents/Eigen maaksels/Verhalen staan buiten bin en in dropbox/radio controlled/content"

df, metadata_dict = process_nwd_files(directory_path)
print("Data extracted and enddates updated. Modify df as needed, then call update_nwd_files().")
print(df)

# After modifying df, call this function to write back changes

df["enddate"] = df["enddate"] + timedelta(days=1)

print(df)
update_nwd_files(directory_path, df, metadata_dict)
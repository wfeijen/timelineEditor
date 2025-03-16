from datetime import datetime, timedelta

class File_handler:
    def __init__(self, path):
        self.path = path
 
    def get_metadata(self):
        metadata = {"chapter": None, "path": None, "plot": "geen_plot", "synopsis": "", "startdate": None, "enddate": None}
        time_values = []
        
        with open(self.path, "r", encoding="utf-8") as file:
            for line in file:
                if line.startswith("%%~name:"):
                    metadata["chapter"] = line.split("%%~name:")[1].strip()
                elif line.startswith("%%~path: 38afc2dd349ba/"):
                    metadata["path"] = self.path.strip()
                elif line.startswith("@plot:"):
                    plot_value = line.split("@plot:")[1].strip()
                    if plot_value:
                        metadata["plot"] = plot_value                
                elif line.startswith("% Synopsis:"):
                    synopsis_value = line.split("% Synopsis:")[1].strip()
                    if synopsis_value:
                        metadata["synopsis"] = synopsis_value
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
    
    def set_metadata(self, metadata):
        with open(self.path, "r", encoding="utf-8") as file:
            lines = file.readlines()                
            # Remove existing @plot: and @time:
        lines = [line for line in lines if not line.startswith("@plot:") and not line.startswith("@time:") and not line.startswith("% Synopsis:")]
        
        # Add new metadata 
        updated_lines = [line for line in lines if False]
        for line in lines:
            updated_lines.append(line)
            if line.startswith("%%~date:"):
                updated_lines.append(f"@plot: {metadata['plot']}\n")
                updated_lines.append(f"@time: {metadata['startdate'].strftime('%Y-%m-%d')}\n")
                updated_lines.append(f"@time: {metadata['enddate'].strftime('%Y-%m-%d')}\n")
                updated_lines.append(f"% Synopsis: {metadata['synopsis']}\n")
        with open(self.path, "w", encoding="utf-8") as file:
            file.writelines(updated_lines)




def main():
    lines = [
            f"@plot: a\n",
            f"@time: b\n",
            f"@time: c\n"
            f"%%~date: d\n"
            f"@plot: e\n",
            f"@time: f\n",
            f"@time: g\n"
        ]

    print(lines)

if __name__ == "__main__":
    main()
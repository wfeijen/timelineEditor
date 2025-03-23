from datetime import datetime, timedelta

class Chapter:
    def __init__(self, path):
        self.path = path
        self.chapter = ""
        self.plot = ""
        self.pov = ""
        self.char = ""
        self.synopsis = ""
        self.startdate = datetime.strptime("2022-01-01", "%Y-%m-%d").date()
        self.enddate = datetime.strptime("2022-01-02", "%Y-%m-%d").date()

        time_values = []
        synopsis_value = None
        plot_value = None
        with open(self.path, "r", encoding="utf-8") as file:
            for line in file:
                if line.startswith("%%~name:"):
                    self.chapter = line.split("%%~name:")[1].strip()
                elif line.startswith("@plot:"):
                    plot_value = line.split("@plot:")[1].strip()
                elif line.startswith("@pov:"):
                    self.pov = line.split("@pov:")[1].strip()
                elif line.startswith("@char:"):
                    self.char = line.split("@char:")[1].strip()
                elif line.startswith("% Synopsis:"):
                    synopsis_value = line.split("% Synopsis:")[1].strip()
                elif line.startswith("@time:"):
                    time_value = line.split("@time:")[1].strip()
                    try:
                        time_values.append(datetime.strptime(time_value, "%Y-%m-%d").date())
                    except ValueError:
                        continue

        if time_values:
            self.startdate = min(time_values)
            self.enddate = max(time_values) if len(time_values) > 1 else (time_values[0] + timedelta(days=1))
        else:
            return None
        if plot_value:
            self.plot = plot_value
        if synopsis_value:
            self.synopsis = synopsis_value   

    
    
    def write(self):
        with open(self.path, "r", encoding="utf-8") as file:
            lines = file.readlines()                
            # Remove existing @plot: and @time:
        lines = [line for line in lines if not line.startswith("@plot:") and not line.startswith("@pov:") and not line.startswith("@char:") and not line.startswith("@time:") and not line.startswith("% Synopsis:")]
        
        # Add new metadata 
        updated_lines = [line for line in lines if False]
        name_not_in_headline_yet = True
        for line in lines:
            # Kop gelijk trekken met naam
            if  line.startswith("#") and name_not_in_headline_yet:                 
                if line.startswith("# "): 
                    updated_lines.append(f"# {self.chapter}\n")
                    name_not_in_headline_yet = False
                elif line.startswith("## "): 
                    updated_lines.append(f"## {self.chapter}\n")
                    name_not_in_headline_yet = False
                elif line.startswith("### "): 
                    updated_lines.append(f"### {self.chapter}\n")
                    name_not_in_headline_yet = False
            else:               
                updated_lines.append(line)
                if line.startswith("%%~date:"):
                    updated_lines.append(f"@plot: {self.plot}\n")
                    updated_lines.append(f"@time: {self.startdate.strftime('%Y-%m-%d')}\n")
                    updated_lines.append(f"@time: {self.enddate.strftime('%Y-%m-%d')}\n")
                    updated_lines.append(f"@pov: {self.pov}\n")
                    updated_lines.append(f"@char: {self.char}\n")
                    updated_lines.append(f"% Synopsis: {self.synopsis}\n")
        with open(self.path, "w", encoding="utf-8") as file:
            file.writelines(updated_lines)

    # def __repr__(self):
    #     return "Test()"
    def __str__(self):
        return f"name: {self.chapter}\n plot: {self.plot}\ntime: {self.startdate.strftime('%Y-%m-%d')}\ntime: {self.enddate.strftime('%Y-%m-%d')}\npov: {self.pov}\nchar: {self.char}\n"


def main():
    print("x")

if __name__ == "__main__":
    main()
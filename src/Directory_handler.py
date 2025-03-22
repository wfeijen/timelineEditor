import os
from File_handler import File_handler

class Directory_handler:
    def __init__(self, directory):
        self.directory = directory
        self.list_files()


    def list_files(self):
        self.file_handlers = {}       
        for filename in os.listdir(self.directory):
            if filename.endswith(".nwd"):
                path = os.path.join(self.directory, filename)
                file_handler = File_handler(path)
                self.file_handlers[path] = file_handler 

    def get_metadata(self):
        self.list_files()

        data = []
        
        for file_handler in self.file_handlers.values():
            metadata = file_handler.get_metadata()
            if metadata:
                data.append(metadata)

        # df_metadata = pd.DataFrame(data, columns=["chapter", "path", "plot", "synopsis", "startdate", "enddate"])
        # df_metadata = df_metadata.sort_values(by=['plot', 'startdate', 'enddate'])
        sorted_data = sorted(data, key=lambda x: (x["plot"], x["startdate"], x["enddate"]))
        
        return sorted_data
    
    def set_metadata(self, df_metadata):
        try:
            for row in df_metadata:
                self.file_handlers[row["path"]].set_metadata(row)
        except KeyError as e:
            print(f"Error: {e}")
            print(row)


def main():
    directory_path = "/home/willem/Documents/Eigen maaksels/Verhalen staan buiten bin en in dropbox/radio controlled/content"
    directory_handler = Directory_handler(directory_path)
    metadata = directory_handler.get_metadata()
    print(metadata)
    directory_handler.set_metadata(metadata)


if __name__ == "__main__":
    main()
import os
from Chapter import Chapter

class Document:
    def __init__(self, directory):
        self.directory = directory
        self.chapters = []
        self.read()


    def read(self):
        self.chapters = []
        for filename in os.listdir(self.directory):
            if filename.endswith(".nwd"):
                path = os.path.join(self.directory, filename)
                chapter = Chapter(path)
                self.chapters.append(chapter)


    def write(self):
        try:
            for chapter in self.chapters:
                chapter.write()
        except KeyError as e:
            print(f"Error: {e}")
            print(chapter)

    def __str__(self):
        res = ""
        for chapter in self.chapters:
            res = res + str(chapter) + "\n\n"
        return res


def main():
    directory_path = "/home/willem/Documents/Eigen maaksels/Verhalen staan buiten bin en in dropbox/radio controlled/content"
    document = Document(directory_path)
    document.read()
    print(document)
    document.write()


if __name__ == "__main__":
    main()

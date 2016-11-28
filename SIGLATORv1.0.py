import tkinter as tk
from tkinter import filedialog
from os import listdir, path, chdir
from PIL import Image

class AppInterface(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.dir_btn = tk.Button(self)
        self.dir_btn["text"] = "Choose a folder"
        self.dir_btn["command"] = self.open_folder
        self.dir_btn.pack(side=tk.LEFT)

        self.logo_btn = tk.Button(self)
        self.logo_btn["text"] = "Choose a logo"
        self.logo_btn["command"] = self.get_logo
        self.logo_btn.pack(side=tk.LEFT)

        self.exe_btn = tk.Button(self)
        self.exe_btn["text"] = "Add logo"
        self.exe_btn["command"] = self.add_logo
        self.exe_btn.pack(side=tk.RIGHT)

    def open_folder(self):
        self.directory = tk.filedialog.askdirectory()

    def get_logo(self):
        self.logoPath = tk.filedialog.askopenfilename()

    def add_logo(self):
        self.get_images()
        self.process_images()

    def get_images(self):
        currentFolder = chdir(self.directory)
        print("Folder path: " + self.directory)
        validImages = [".jpg", ".jpeg", ".bmp", ".png", ".gif"]
        self.images = []
        for file in listdir(currentFolder):
            ext = path.splitext(file)[1]
            if ext.lower() in validImages:
                self.images.append(path.abspath(file))

    def process_images(self):

        self.logo = Image.open(self.logoPath)
        logo_width, logo_height = self.logo.size[0], self.logo.size[1]

        im = Image.open(self.images[0])
        print(im.size, im.format)
        image_width, image_height = im.size[0], im.size[1]

        box = (image_width - logo_width, image_height - logo_height, image_width, image_height)

        self.logo.load()
        im.paste(self.logo, box, mask=self.logo.split()[3])
        im.show()



        '''for image in self.images:
            print(image)
            im = Image.open(image)
            print(im.size, im.format)
            width = im.size[0]
            height = im.size[1]'''

def main():
    root = tk.Tk()
    app = AppInterface(master=root)
    app.mainloop()

main()
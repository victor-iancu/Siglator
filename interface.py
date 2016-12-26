#!python3
import images as imgModule
import tkinter as tk
import threading
import time
import cProfile
from tkinter import filedialog, messagebox, ttk
from os import listdir, path, chdir
from distutils.core import setup
import multiprocessing


def is_image(image_path):
    validImages = [".jpg", ".jpeg", ".bmp", ".png", ".gif"]
    extension = path.splitext(image_path)[1]
    if extension.lower() in validImages:
        return True
    return False


def get_images(directory_path):
    currentFolder = chdir(directory_path)
    print("Folder path: " + directory_path)
    validImages = [".jpg", ".jpeg", ".bmp", ".png", ".gif"]
    gui.images = []
    for file in listdir(currentFolder):
        ext = path.splitext(file)[1]
        if ext.lower() in validImages:
            gui.images.append(path.abspath(file))


class FolderThread(threading.Thread):
    def __init__(self, directory_path):
        threading.Thread.__init__(self)
        self.daemon = True
        self.directory_path = directory_path

    def run(self):
        print("Started FolderThread ")
        # get files from directory
        get_images(self.directory_path)
        print("Finished FolderThread ")


class AddLogoThread(threading.Thread):
    def __init__(self, images_paths, logo_path, save_directory, logo_priority):
        threading.Thread.__init__(self)
        self.daemon = True
        self.images_paths = images_paths
        self.logo_path = logo_path
        self.save_directory = save_directory + "/SIGLATOR Results"
        self.logo_priority = logo_priority

    def run(self):
        print("Started AddLogoThread ")
        start_time = time.time()
        imgModule.apply_logo(self.images_paths, self.logo_path,
                             self.save_directory, self.logo_priority )


        '''#--- cProfile ---
        fileName = "test.txt"
        cProfile.runctx("imgModule.test_apply_logo(img,logo,dir)", globals(),
                        {
                            'img': self.images_paths,
                            'logo': self.logo_path,
                            'dir': self.save_directory + "/SIGLATOR Results"
                        },
                        fileName)'''


        end_time = time.time()
        print("Duration: ",end_time - start_time)
        print("Finished AddLogoThread ")


class DDList(tk.Listbox):
    """ A Tkinter listbox with drag'n'drop reordering of entries. """
    def __init__(self, master, **kw):
        kw['selectmode'] = tk.EXTENDED
        kw['activestyle'] = tk.NONE
        tk.Listbox.__init__(self, master, kw)
        self.bind('<Button-1>', self.setCurrent)
        self.bind('<B1-Motion>', self.shiftSelection)
        self.curIndex = None
    def setCurrent(self, event):
        self.curIndex = self.nearest(event.y)
    def shiftSelection(self, event):
        i = self.nearest(event.y)
        if i < self.curIndex:
            x = self.get(i)
            self.delete(i)
            self.insert(i+1, x)
            self.curIndex = i
        elif i > self.curIndex:
            x = self.get(i)
            self.delete(i)
            self.insert(i-1, x)
            self.curIndex = i


class AppInterface(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        #inits
        self.directory_path = None
        self.logo_path = None
        self.images = []
        self.priority_dict = {"Bottom right": 1,
                              "Bottom left": 2,
                              "Top right": 3,
                              "Top left": 4}
        #drawing the interface
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.directory_btn = tk.Button(self)
        self.directory_btn["text"] = "Choose a folder"
        self.directory_btn["command"] = self.open_folder
        self.directory_btn.grid(row=0, column=0, sticky=tk.W + tk.E, padx=2, pady=1)

        self.directory_text = tk.Text(self)
        self.directory_text.insert(tk.END, "No chosen directory...")
        self.directory_text.config(state=tk.DISABLED, height=1)
        self.directory_text.grid(row=0, column=1, padx=2, pady=1)

        self.logo_btn = tk.Button(self)
        self.logo_btn["text"] = "Choose a logo"
        self.logo_btn["command"] = self.get_logo
        self.logo_btn.grid(row=1, column=0, sticky=tk.W + tk.E, padx=2, pady=1)

        self.logo_text = tk.Text(self)
        self.logo_text.insert(tk.END, "No chosen logo...")
        self.logo_text.config(state=tk.DISABLED, height=1)
        self.logo_text.grid(row=1, column=1, padx=2, pady=1)

        self.listbox = DDList(self)
        self.listbox.grid(row=2, column=0)

        #init listbox
        for item in ["Bottom right", "Bottom left", "Top right", "Top left"]:
            self.listbox.insert(tk.END, item)

        self.add_logo_btn = tk.Button(self)
        self.add_logo_btn["text"] = "Add Logo"
        self.add_logo_btn["command"] = self.add_logo
        self.add_logo_btn.config(state=tk.NORMAL)
        self.add_logo_btn.grid(row=4, columnspan=2, pady=10)

        self.image_preview_canvas = tk.Canvas(self, width=0, height=0)
        self.image_preview_canvas.grid(row=5, columnspan=2)

    def open_folder(self):
        self.directory_path = tk.filedialog.askdirectory()
        if not self.directory_path:
            messagebox.showinfo("Info", "No directory chosen")
        else:
            # display directory name
            self.directory_text.config(state=tk.NORMAL)
            self.directory_text.delete(1.0, tk.END)
            self.directory_text.insert(tk.END, self.directory_path)
            self.directory_text.config(state=tk.DISABLED)
            folder_thread = FolderThread(self.directory_path)
            folder_thread.start()

    def get_logo(self):
        self.logo_path = tk.filedialog.askopenfilename()
        if not is_image(self.logo_path):
            messagebox.showwarning("Warning", "Chosen file is not an image!")
        else:
            # display chosen logo
            self.logo_text.config(state=tk.NORMAL)
            self.logo_text.delete(1.0, tk.END)
            self.logo_text.insert(tk.END, path.split(self.logo_path)[1])
            self.logo_text.config(state=tk.DISABLED)

    def add_logo(self):
        logo_priority = list(map((lambda item: self.priority_dict[item]),self.listbox.get(0, tk.END)))
        print(logo_priority)
        add_logo_thread = AddLogoThread(self.images, self.logo_path, self.directory_path, logo_priority)
        add_logo_thread.start()

if __name__ == "__main__":
    multiprocessing.freeze_support()
    root = tk.Tk()
    gui = AppInterface(master=root)
    gui.mainloop()

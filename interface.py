#!python3
import images as imgModule
import tkinter as tk
import argparse
import threading
import time
import multiprocessing
import sys
import cProfile
from tkinter import filedialog, messagebox, ttk
from os import listdir, path, chdir
from PIL import ImageTk as ImgTk


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
    images = []
    for file in listdir(currentFolder):
        ext = path.splitext(file)[1]
        if ext.lower() in validImages:
            images.append(path.abspath(file))
    return images


class FolderThread(threading.Thread):
    def __init__(self, directory_path):
        threading.Thread.__init__(self)
        self.daemon = True
        self.directory_path = directory_path

    def run(self):
        print("Started FolderThread ")
        # get files from directory
        gui.images = get_images(self.directory_path)
        print("Finished FolderThread ")


class ProgressThread(threading.Thread):
    def __init__(self, id, progressbar_queue, length=0):
        threading.Thread.__init__(self)
        self.id = id
        self.progressbar_queue = progressbar_queue
        self.length = length

    def run(self):
        print("Started ProgressThread ")
        if self.id == "GUI":
            progress_func = gui.update_progress_bar
        else:
            progress_func = progress_bar_cmd

        count = 0

        while True:
            try:
                x = self.progressbar_queue.get(True)
                if x == "DONE":
                    break
                count += 1
                progress_func(count, self.length)
            except:
                pass
        print("Finished ProgressThread ")


class AddLogoThread(threading.Thread):
    def __init__(self, images_paths, logo_path, save_directory,
                 logo_priority, offsets, progress_queue):
        threading.Thread.__init__(self)
        #self.daemon = True
        self.images_paths = images_paths
        self.logo_path = logo_path
        self.save_directory = save_directory + "/SIGLATOR Results"
        self.logo_priority = logo_priority
        self.offsets = offsets
        self.progress_queue = progress_queue

    def run(self):
        print("Started AddLogoThread ")
        start_time = time.time()

        imgModule.apply_logo(self.images_paths, self.logo_path,
                             self.save_directory, self.logo_priority,
                             self.offsets, self.progress_queue)
        self.progress_queue.put_nowait("DONE")
        # cProfile
        '''
        fileName = "test.txt"
        cProfile.runctx("imgModule.test_apply_logo(img,logo,dir)", globals(),
                        {
                            'img': self.images_paths,
                            'logo': self.logo_path,
                            'dir': self.save_directory + "/SIGLATOR Results"
                        },
                        fileName)
        '''
        try:
            gui.progress_bar.grid_forget()
        except:
            pass

        end_time = time.time()
        print()
        print("Duration: ", end_time - start_time)
        print("Finished AddLogoThread ")


class PreviewThread(threading.Thread):
    def __init__(self, images_paths, logo_path, logo_priority, current_photo, offsets):
        threading.Thread.__init__(self)
        self.images_paths = images_paths
        self.logo_path = logo_path
        self.logo_priority = logo_priority
        self.current_photo = current_photo
        self.offsets = offsets

    def run(self):
        print("Started PreviewThread ")
        image = imgModule.preview_images(self.images_paths, self.logo_path,
                                         self.logo_priority, self.current_photo,
                                         self.offsets)
        gui.display_new_image(image)
        print("Finished PreviewThread ")


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
            self.insert(i + 1, x)
            self.curIndex = i
        elif i > self.curIndex:
            x = self.get(i)
            self.delete(i)
            self.insert(i - 1, x)
            self.curIndex = i


class AppInterface(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)

        # inits
        self.directory_path = None
        self.logo_path = None
        self.images = []
        self.priority_dict = {"Bottom right": 1,
                              "Bottom left": 2,
                              "Top right": 3,
                              "Top left": 4}
        self.current_photo_index = 0
        self.current_photo = None
        self.logo_scale = tk.DoubleVar()
        self.logo_horizontal_offset = tk.DoubleVar()
        self.logo_vertical_offset = tk.DoubleVar()
        self.progress_bar = None
        self.progress_bar_value = tk.IntVar()

        # drawing the interface
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.directory_btn = ttk.Button(self)
        self.directory_btn["text"] = "Choose a folder"
        self.directory_btn["command"] = self.open_folder
        self.directory_btn.grid(row=0, column=0, sticky=tk.W + tk.E, padx=2, pady=1)

        self.directory_text = tk.Text(self)
        self.directory_text.insert(tk.END, "No chosen directory...")
        self.directory_text.config(state=tk.DISABLED, height=1)
        self.directory_text.grid(row=0, column=1, padx=2, pady=1)

        self.logo_btn = ttk.Button(self)
        self.logo_btn["text"] = "Choose a logo"
        self.logo_btn["command"] = self.get_logo
        self.logo_btn.grid(row=1, column=0, sticky=tk.W + tk.E, padx=2, pady=1)

        self.logo_text = tk.Text(self)
        self.logo_text.insert(tk.END, "No chosen logo...")
        self.logo_text.config(state=tk.DISABLED, height=1)
        self.logo_text.grid(row=1, column=1, padx=2, pady=1)

        # logo customization Frame
        self.logo_customize_frame = ttk.Frame(self)
        self.logo_customize_frame.grid(row=2, columnspan=2, sticky=tk.W)

        self.listbox = DDList(self.logo_customize_frame)
        self.listbox.grid(rowspan=3, column=0)

        # init listbox
        for item in ["Bottom right", "Bottom left", "Top right", "Top left"]:
            self.listbox.insert(tk.END, item)

        # default offsets
        self.logo_scale.set(30)
        self.logo_horizontal_offset.set(3)
        self.logo_vertical_offset.set(3)

        self.logo_scale_label = ttk.Label(self.logo_customize_frame,
                                          text="Logo scale:")
        self.logo_scale_label.grid(row=0, column=1)
        self.logo_scale_scale = ttk.Scale(self.logo_customize_frame,
                                         from_=0, to=100,
                                         orient=tk.HORIZONTAL,
                                         variable=self.logo_scale)
        self.logo_scale_scale.grid(row=0, column=2)

        self.logo_horizontal_offset_label = ttk.Label(self.logo_customize_frame,
                                                      text="Horizontal offset:")
        self.logo_horizontal_offset_label.grid(row=1, column=1)
        self.logo_horizontal_offset_scale = ttk.Scale(self.logo_customize_frame,
                                                       from_=0, to=100,
                                                       orient=tk.HORIZONTAL,
                                                       variable=self.logo_horizontal_offset)
        self.logo_horizontal_offset_scale.grid(row=1, column=2)

        self.logo_vertical_offset_label = ttk.Label(self.logo_customize_frame,
                                                    text="Vertical offset:")
        self.logo_vertical_offset_label.grid(row=2, column=1)
        self.logo_vertical_offset_scale = ttk.Scale(self.logo_customize_frame,
                                                   from_=0, to=100,
                                                   orient=tk.HORIZONTAL,
                                                   variable=self.logo_vertical_offset)
        self.logo_vertical_offset_scale.grid(row=2, column=2)

        # functionality buttons frame
        self.add_logo_btn = ttk.Button(self)
        self.add_logo_btn["text"] = "Add Logo"
        self.add_logo_btn["command"] = self.add_logo
        self.add_logo_btn.grid(row=4, column=0, pady=10)

        self.preview_btn = ttk.Button(self)
        self.preview_btn["text"] = "Preview"
        self.preview_btn["command"] = self.preview
        self.preview_btn.grid(row=4, column=1)

        # preview images frame
        self.image_preview_canvas = tk.Canvas(self, width=0, height=0)
        self.image_preview_canvas.grid(row=5, columnspan=2)

        self.previous_btn = ttk.Button(self)
        self.previous_btn["text"] = "Prev"
        self.previous_btn["command"] = self.previous
        self.previous_btn.grid(row=6, column=0)

        self.next_btn = ttk.Button(self)
        self.next_btn["text"] = "Next"
        self.next_btn["command"] = self.next
        self.next_btn.grid(row=6, column=1)

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
        logo_priority = list(map((lambda item: self.priority_dict[item]), self.listbox.get(0, tk.END)))

        self.progress_bar = ttk.Progressbar(self, maximum=len(self.images))
        self.progress_bar.grid(row=7, columnspan=2, stick=tk.W + tk.E)

        process_manager = multiprocessing.Manager()
        pbar_queue = process_manager.Queue()
        progress_thread = ProgressThread("GUI", pbar_queue)
        add_logo_thread = AddLogoThread(self.images, self.logo_path,
                                        self.directory_path, logo_priority,
                                        (self.logo_scale.get(),
                                         self.logo_horizontal_offset.get(),
                                         self.logo_vertical_offset.get()),
                                        pbar_queue)
        add_logo_thread.start()
        progress_thread.start()

    def preview(self):
        # self.image_preview_canvas.delete("all")
        self.image_preview_canvas.create_text(480, 270, text="Loading...", font=("Purisa", 50), fill="orange")
        logo_priority = list(map((lambda item: self.priority_dict[item]), self.listbox.get(0, tk.END)))
        preview_thread = PreviewThread(self.images, self.logo_path,
                                       logo_priority, self.current_photo_index,
                                       (int(round(self.logo_scale.get())),
                                        int(round(self.logo_horizontal_offset.get())),
                                        int(round(self.logo_vertical_offset.get()))))
        preview_thread.start()

    def display_new_image(self, image):
        self.current_photo = ImgTk.PhotoImage(image)
        self.image_preview_canvas.delete("all")
        self.image_preview_canvas.config(width=960, height=540)
        self.image_preview_canvas.create_image(480, 270, image=self.current_photo)

    def previous(self):
        try:
            if self.current_photo_index == 0:
                self.current_photo_index = len(self.images) - 1
            else:
                self.current_photo_index -= 1
            self.preview()
        except:
            print("Can't get previous photo")

    def next(self):
        try:
            if self.current_photo_index == len(self.images) - 1:
                self.current_photo_index = 0
            else:
                self.current_photo_index += 1
            self.preview()
        except:
            print("Can't get next photo")

    def update_progress_bar(self, *args):
        self.progress_bar.step()
        self.progress_bar.update()


def get_parser():
    parser = argparse.ArgumentParser(description='add logos to photos',
                                     formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('--directory', '-D',
                        help='path to the directory')

    parser.add_argument('--logo', '-L',
                        help="path to the logo")

    parser.add_argument('--priority', '-P', nargs=4, type=int,
                        help=
'''
logo's position (corner) priority
4 integers (1-4); each representing a corner:
1 - bottom-right
2 - bottom-left
3 - top-right
4 - top-left
default: (1,2,3,4)
'''
                        )

    parser.add_argument('--scale', '-S', nargs=3, type=int,
                        help=
'''
logo's scale and position (offsets)
3 integers, each representing a percentage(0-100):
first integer: logo's scale
second integer: logo's horizontal offset
third integer: logo's vertical offset
default: (30, 3, 3)
'''
                        )
    return parser

def command_line(args):

    try:
        directory_path = args.directory
        images_paths = get_images(directory_path)
        logo_path = args.logo

        if not args.scale:
            offsets = (30, 3, 3) # default
        else:
            offsets = args.scale

        if not args.priority:
            logo_priority = (1, 2, 3, 4) # default
        else:
            logo_priority = args.priority

        process_manager = multiprocessing.Manager()
        progressbar_queue = process_manager.Queue()
        progress_thread = ProgressThread("CMD", progressbar_queue, len(images_paths))

        add_logo_thread = AddLogoThread(images_paths, logo_path,
                                    directory_path, logo_priority,
                                    offsets, progressbar_queue)
        add_logo_thread.start()
        progress_thread.start()
    except:
        print("Not enough arguments")


def progress_bar_cmd(count, total, suffix=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', suffix))
    sys.stdout.flush()


if __name__ == "__main__":
    # build support for processes
    multiprocessing.freeze_support()

    parser = get_parser()
    args = parser.parse_args()

    if args.directory and args.logo:
        command_line(args)
    else:
        # gui
        root = tk.Tk()
        root.style = ttk.Style()
        root.style.theme_use('xpnative')
        root.wm_title("Siglator")
        gui = AppInterface(master=root)
        gui.mainloop()

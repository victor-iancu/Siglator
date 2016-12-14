import tkinter as tk
import threading
import queue
import time
import multiprocessing
from tkinter import filedialog, messagebox, ttk
from os import listdir, path, chdir, makedirs
from PIL import Image, ImageTk as ImgTk
from colorthief import ColorThief
from io import BytesIO


class G:
    # dir related
    directory_path = None
    images = None

    # logo related
    logo_path = None
    logo = None
    logo_width = None
    logo_height = None
    logo_dominant_color = None

    # image related
    preview_image = None
    logo_priority = [1,2,3,4]
    image_save_path = None

    # threads related
    preview_exit_flag = 1
    cpu_count = multiprocessing.cpu_count()

    # test purposes
    count = 0
    time_per_image_average = 0


def is_image(image_path):
    validImages = [".jpg", ".jpeg", ".bmp", ".png", ".gif"]
    extension = path.splitext(image_path)[1]
    if extension.lower() in validImages:
        return True
    return False


def get_dominant_color(image_reference, quality=10):
    color_thief = ColorThief(image_reference)
    return color_thief.get_color(quality=quality)


def get_images(directory_path):
    currentFolder = chdir(directory_path)
    print("Folder path: " + directory_path)
    validImages = [".jpg", ".jpeg", ".bmp", ".png", ".gif"]
    G.images = []
    for file in listdir(currentFolder):
        ext = path.splitext(file)[1]
        if ext.lower() in validImages:
            G.images.append(path.abspath(file))
            images_queue.put(path.abspath(file))


def verify_compatibility(section, accuracy=5):
    width, height = section.size
    width_step = int(width / accuracy)

    # print("Logo dominant color: ", G.logo_dominant_color)

    for i in range(accuracy):

        box = (width_step * i, 0, width_step * (i + 1), height)
        temp_section = section.crop(box)

        bytesIO = BytesIO()
        temp_section.save(bytesIO, 'JPEG')
        bytesIO.seek(0)

        try:
            temp_section_dominant_color = get_dominant_color(bytesIO)
            #print("CT Spot dominant color: ", temp_section_dominant_color)
            if not verify_color(temp_section_dominant_color):
                return False
        except:
            pass

        bytesIO.close()
    return True


def verify_color(section_dom_color_rgb):
    section_r, section_g, section_b = section_dom_color_rgb

    for index in range(3):
        if (abs(section_dom_color_rgb[index] - G.logo_dominant_color[index]) >= 60):
            return True

    if abs(section_r - section_g) >= 30 and abs(section_r - section_b) >= 30:
        return True

    if abs(section_r - section_b) >= 30 and abs(section_r - section_g) >= 30:
        return True

    if abs(section_g - section_b) >= 30 and abs(section_g - section_r) >= 30:
        return True

    return False


class Photo:
    def __init__(self, image_path):
        self.save_path = G.image_save_path + "/" + path.split(image_path)[1]
        self.image = Image.open(image_path)
        self.logo = Image.open(G.logo_path)
        self.width, self.height = self.image.size

        # set logo's width and height pixel beginning points
        self.section_left_offset = int(self.width * 70 / 100)
        self.section_top_offset = int(self.height * 70 / 100)

        # set logo's width and height pixel ending points
        self.section_right_offset = int(self.width * 3 / 100)
        self.section_bottom_offset = int(self.height * 3 / 100)

        # size to scale the logo to
        logo_scale_box = (self.width - self.section_left_offset - self.section_right_offset,
                          self.height - self.section_top_offset - self.section_bottom_offset)

        # scale logo
        #G.logo.thumbnail(logo_scale_box, Image.ANTIALIAS)
        self.logo.thumbnail(logo_scale_box, Image.ANTIALIAS)

        # scaled logo dimensions
        self.scaled_logo_width, self.scaled_logo_height = self.logo.size

        # dictionary for indexing functions
        self.logo_pos_index = {1: self.get_bottom_right_corner,
                               2: self.get_bottom_left_corner,
                               3: self.get_top_right_corner,
                               4: self.get_top_left_corner}

    def apply_logo(self):
        self.image.paste(self.logo, self.box, mask=self.logo.split()[3])
        self.image.save(self.save_path)
        #print("Image saved: ", self.save_path)

    def get_bottom_right_corner(self):
        # bottom-right box
        self.box = (self.width - self.scaled_logo_width - self.section_right_offset,
                    self.height - self.scaled_logo_height - self.section_bottom_offset)

        temp_box = (self.width - self.scaled_logo_width - self.section_right_offset,
                    self.height - self.scaled_logo_height - self.section_bottom_offset,
                    self.width - self.section_right_offset,
                    self.height - self.section_bottom_offset)

        section = self.image.crop(temp_box)
        return section

    def get_bottom_left_corner(self):
        # bottom-left box
        self.box = (self.section_right_offset,
                    self.height - self.scaled_logo_height - self.section_bottom_offset)

        temp_box = (self.section_right_offset,
                    self.height - self.scaled_logo_height - self.section_bottom_offset,
                    self.section_right_offset + self.scaled_logo_width,
                    self.height - self.section_bottom_offset)

        section = self.image.crop(temp_box)
        return section

    def get_top_right_corner(self):
        # top-right box
        self.box = (self.width - self.scaled_logo_width - self.section_right_offset,
                    self.section_bottom_offset)

        temp_box = (self.width - self.scaled_logo_width - self.section_right_offset,
                    self.section_bottom_offset,
                    self.width - self.section_right_offset,
                    self.section_bottom_offset + self.scaled_logo_height)

        section = self.image.crop(temp_box)
        return section

    def get_top_left_corner(self):
        # top-left box
        self.box = (self.section_right_offset,
                    self.section_bottom_offset)

        temp_box = (self.section_right_offset,
                    self.section_bottom_offset,
                    self.section_right_offset + self.scaled_logo_width,
                    self.section_bottom_offset + self.scaled_logo_height)

        section = self.image.crop(temp_box)
        return section

class FolderThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        print("Started FolderThread ")
        if not G.directory_path:
            messagebox.showinfo("Info", "No directory chosen")
        else:
            # display directory name
            gui.directory_text.config(state=tk.NORMAL)
            gui.directory_text.delete(1.0, tk.END)
            gui.directory_text.insert(tk.END, G.directory_path)
            gui.directory_text.config(state=tk.DISABLED)
            # add to image save path
            G.image_save_path = G.directory_path + '/Siglator Results'
            # get files from directory
            get_images(G.directory_path)
            # add directory to queue
            # ID 1 for directory
            preview_queue.put(1)

        print("Finished FolderThread ")


class LogoThread(threading.Thread):
    def __init__(self, path):
        threading.Thread.__init__(self)
        self.path = path

    def run(self):
        print("Started LogoThread ")
        if not is_image(self.path):
            messagebox.showwarning("Warning", "Chosen file is not an image!")
        else:
            # display chosen logo
            gui.logo_text.config(state=tk.NORMAL)
            gui.logo_text.delete(1.0, tk.END)
            gui.logo_text.insert(tk.END, path.split(self.path)[1])
            gui.logo_text.config(state=tk.DISABLED)

            # get logo's reference, resolution and dominant RGB
            G.logo = Image.open(self.path)
            G.logo_width, G.logo_height = G.logo.size
            G.logo_dominant_color = get_dominant_color(self.path)

            # add logo to queue
            # ID 2 for logo
            preview_queue.put(2)
        print("Finished LogoThread ")


class PreviewThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        print("Started PreviewThread ")
        temp = []
        while G.preview_exit_flag:
            if preview_queue.empty():
                time.sleep(1.5)
                # print("Waiting")
            else:
                temp.append(preview_queue.get())
                if 1 in temp and 2 in temp:
                    try:
                        temp_photo = Image.open(G.images[0])
                        thumb_dim = (960, 540)
                        temp_photo.thumbnail(thumb_dim, Image.ANTIALIAS)
                        G.preview_image = ImgTk.PhotoImage(temp_photo)
                        gui.image_preview_canvas.delete("all")
                        gui.image_preview_canvas.config(width=960, height=540)
                        gui.image_preview_canvas.create_image(480, 270, image=G.preview_image)
                        gui.add_logo_btn.config(state=tk.NORMAL)
                    except:
                        messagebox.showwarning("Warning", "There are no images in the selected folder!")
                        gui.image_preview_canvas.delete("all")
                        gui.image_preview_canvas.config(width=0, height=0)
                        gui.add_logo_btn.config(state=tk.DISABLED)

        print("Finished PreviewThread ")


class ImageThread(threading.Thread):
    def __init__(self, id):
        threading.Thread.__init__(self)
        self.id = id

    def run(self):
        #print("Started ImageThread: ", self.id)

        while not images_queue.empty():
            start_time = time.time()
            path = images_queue.get()
            image = Photo(path)
            for i in G.logo_priority:
                section = image.logo_pos_index[i]()
                if verify_compatibility(section):
                    image.apply_logo()
                    end_time = time.time()
                    G.time_per_image_average += end_time-start_time
                    print("Time elapsed: ", end_time - start_time)
                    break


        #print("Finished ImageThread: ", self.id)



class AddLogoThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        print("Started AddLogoThread ")
        try:
            makedirs(G.image_save_path, exist_ok=True)
            for i in range(G.cpu_count):
                G.count += 1
                temp_reference = ImageThread(G.count)
                temp_reference.start()
        except:
            print("Error at creating new directory!")

        print("Finished AddLogoThread ")


class AppInterface(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
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

        self.add_logo_btn = tk.Button(self)
        self.add_logo_btn["text"] = "Add Logo"
        self.add_logo_btn["command"] = self.add_logo
        self.add_logo_btn.config(state=tk.DISABLED)
        self.add_logo_btn.grid(row=4, columnspan=2, pady=10)

        self.image_preview_canvas = tk.Canvas(self, width=0, height=0)
        self.image_preview_canvas.grid(row=5, columnspan=2)

    def open_folder(self):
        G.directory_path = tk.filedialog.askdirectory()
        folder_thread = FolderThread()
        folder_thread.start()

    def get_logo(self):
        G.logo_path = tk.filedialog.askopenfilename()
        logo_thread = LogoThread(G.logo_path)
        logo_thread.start()

    def add_logo(self):
        add_logo_thread = AddLogoThread()
        add_logo_thread.start()


# preview Photo init
preview_queue = queue.Queue()
preview_thread = PreviewThread()
preview_thread.start()

# images Queue init
images_queue = queue.Queue()

# thread locker init
thread_lock = threading.Lock()

# GUI init
root = tk.Tk()
gui = AppInterface(master=root)
gui.mainloop()

# exiting preview thread
G.preview_exit_flag = 0

print("Performance average: ", G.time_per_image_average/len(G.images))

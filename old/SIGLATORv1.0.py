import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from os import listdir, path, chdir, makedirs
from PIL import Image, ImageTk as ImgTk
from colorthief import ColorThief
from io import BytesIO

class Photo(Image):

    def __init__(self, path):
        super.__init__(self)
        self.image = Image.open(path)

    def get_dominant_color (self, image):
        color_thief = ColorThief(image)
        return color_thief.get_color(quality=10)

    def get_bottom_right_corner(self,):
        print("BR")

    def get_bottom_left_corner(self):
        print("BL")

    def get_top_right_corner(self):
        print("TR")

    def get_top_left_corner(self):
        print("TL")

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

        self.radio_var = tk.IntVar()
        self.radio_var.set(1)

        self.preview_radio_btn = tk.Radiobutton(self)
        self.preview_radio_btn["text"] = "Preview photos"
        self.preview_radio_btn["variable"] = self.radio_var
        self.preview_radio_btn["value"] = 1
        self.preview_radio_btn.grid(row=2, column=0, sticky=tk.W)

        self.save_radio_btn = tk.Radiobutton(self)
        self.save_radio_btn["text"] = "Save photos"
        self.save_radio_btn["variable"] = self.radio_var
        self.save_radio_btn["value"] = 2
        self.save_radio_btn.grid(row=3, column=0, sticky=tk.W)

        self.add_logo_btn = tk.Button(self)
        self.add_logo_btn["text"] = "Add Logo"
        self.add_logo_btn["command"] = self.add_logo
        self.add_logo_btn.config(state=tk.DISABLED)
        self.add_logo_btn.grid(row=4, columnspan=2, pady=10)

        self.image_preview_canvas = tk.Canvas(self, width = 0, height = 0)
        self.image_preview_canvas.grid(row=5, columnspan=2)

    def open_folder(self):
        self.directory = tk.filedialog.askdirectory()
        if not self.directory:
            messagebox.showinfo("Info", "No directory chosen")
        else:
            self.directory_text.config(state=tk.NORMAL)
            self.directory_text.delete(1.0, tk.END)
            self.directory_text.insert(tk.END, self.directory)
            self.directory_text.config(state=tk.DISABLED)
            try:
                self.unlock_and_preview()
            except:
                pass

    def get_logo(self):
        logoPath = tk.filedialog.askopenfilename()
        if not self.is_image(logoPath):
            messagebox.showwarning("Warning", "Chosen file is not an image!")
        else:
            # display chosen logo
            self.logo_text.config(state=tk.NORMAL)
            self.logo_text.delete(1.0, tk.END)
            self.logo_text.insert(tk.END, path.split(logoPath)[1])
            self.logo_text.config(state=tk.DISABLED)

            # get logo's dominant RGB
            ct = ColorThief(logoPath)
            self.logo_dominant_color = ct.get_color(quality=5)
            self.logo = Image.open(logoPath)

            try:
                self.unlock_and_preview()
            except:
                pass

    def add_logo(self):
        self.get_images()
        self.progress_bar = ttk.Progressbar(self, maximum=len(self.images))
        #print(self.progress_bar["length"])
        self.progress_bar.grid(row=6, columnspan=2, stick=tk.W+tk.E)
        self.process_images()

    def unlock_and_preview(self):
        if self.directory and self.logo:
            self.add_logo_btn.config(state=tk.NORMAL)
            #verify for photo preview
            #if self.images:
            self.get_images(sample=True)
            print("Preview image triggered")
            print(self.image_sample)
            if self.image_sample:
                temp_photo = Image.open(self.image_sample)
                temp_photo = self.paste_logo(temp_photo)
                #w, h = temp_photo.size
                #print(tk.Frame.winfo_screenwidth(self))
                #print(tk.Frame.winfo_screenheight(self))
                thumb_dim = (960, 540)
                temp_photo.thumbnail(thumb_dim, Image.ANTIALIAS)
                self.preview_image = ImgTk.PhotoImage(temp_photo)
                self.image_preview_canvas.config(width=960, height=540)
                self.image_preview_canvas.create_image(480, 270, image=self.preview_image)
                #self.image_preview_canvas.config(state=tk.NORMAL)

    def is_image(self, image_path):
        validImages = [".jpg", ".jpeg", ".bmp", ".png", ".gif"]
        extension = path.splitext(image_path)[1]
        if extension.lower() in validImages:
            return True
        return False

    def get_images(self, sample=False):
        currentFolder = chdir(self.directory)
        print("Folder path: " + self.directory)
        validImages = [".jpg", ".jpeg", ".bmp", ".png", ".gif"]
        if sample:
            for file in listdir(currentFolder):
                ext = path.splitext(file)[1]
                if ext.lower() in validImages:
                    self.image_sample = path.abspath(file)
                    break
        else:
            self.images = []
            for file in listdir(currentFolder):
                ext = path.splitext(file)[1]
                if ext.lower() in validImages:
                    self.images.append(path.abspath(file))

    '''def get_dominant_color(self, image):
        width, height = image.size
        r_average = 0
        g_average = 0
        b_average = 0

        for x in range(0, width):
            for y in range(0, height):
                r, g, b = image.getpixel((x, y))
                r_average = (r + r_average) / 2
                g_average = (g + g_average) / 2
                b_average = (b + b_average) / 2

        return (int(r_average), int(g_average), int(b_average))
    '''
    '''
    def get_logo_dominant_color(self, image):
            width, height = image.size
            r_average = 0
            g_average = 0
            b_average = 0
            a_average = 0

            for x in range(0, width):
                for y in range(0, height):
                    r, g, b, a = image.getpixel((x, y))
                    r_average = (r + r_average) / 2
                    g_average = (g + g_average) / 2
                    b_average = (b + b_average) / 2
                    a_average = (a + a_average) / 2

            return (int(r_average), int(g_average), int(b_average), int(a_average))
    '''

    def verify_compatibility(self, section, accuracy=5):

        width, height = section.size
        width_step = int(width / accuracy)

        print("Logo dominant color: ", self.logo_dominant_color)

        for i in range(accuracy):

            box = (width_step * i, 0, width_step * (i + 1), height)
            temp_section = section.crop(box)

            bytesIO = BytesIO()
            temp_section.save(bytesIO, 'JPEG')
            bytesIO.seek(0)

            ct = ColorThief(bytesIO)
            try:
                temp_section_dominant_color = ct.get_color(quality=5)
                # my_dominant_rgb = self.get_dominant_color(temp_section)
            except:
                # print("Exception")
                return False
            print("CT Spot dominant color: ", temp_section_dominant_color)
            # print("MY Spot dominant color: ", my_dominant_rgb)
            if not self.verify_color(temp_section_dominant_color):
                return False
            bytesIO.close()
        return True

    def verify_color(self, section_dom_color_rgb):
        section_r, section_g, section_b = section_dom_color_rgb

        for index in range(3):
            if (abs(section_dom_color_rgb[index] - self.logo_dominant_color[index]) >= 60):
                return True

        if abs(section_r - section_g) >= 30 and abs(section_r - section_b) >= 30:
            return True

        if abs(section_r - section_b) >= 30 and abs(section_r - section_g) >= 30:
            return True

        if abs(section_g - section_b) >= 30 and abs(section_g - section_r) >= 30:
            return True

        return False

    
    def paste_logo(self, im):
        # get and store current image's width and height
        image_width, image_height = im.size

        # set logo's width and height pixel beginning points
        image_width_begin_pixel = int(image_width * 70 / 100)
        image_height_begin_pixel = int(image_height * 70 / 100)

        # set logo's width and height pixel ending points
        image_width_end_pixel = int(image_width * 3 / 100)
        image_height_end_pixel = int(image_height * 3 / 100)

        # size to scale the logo to
        max_logo_size = (image_width - image_width_begin_pixel - image_width_end_pixel,
                         image_height - image_height_begin_pixel - image_height_end_pixel)

        # scale logo
        self.logo.thumbnail(max_logo_size, Image.ANTIALIAS)

        # get width and height for the scaled logo
        logo_width, logo_height = self.logo.size

        # bottom-right box
        box = (image_width - logo_width - image_width_end_pixel,
               image_height - logo_height - image_height_end_pixel)

        temp_box = (image_width - logo_width - image_width_end_pixel,
                    image_height - logo_height - image_height_end_pixel,
                    image_width - image_width_end_pixel,
                    image_height - image_height_end_pixel)

        section = im.crop(temp_box)

        if self.verify_compatibility(section, 10):
            print("Logo applied bottom-right!")
        else:
            print("Logo NOT to be applied bottom-right!")
            # bottom-left box
            box = (image_width_end_pixel,
                   image_height - logo_height - image_height_end_pixel)

            temp_box = (image_width_end_pixel,
                        image_height - logo_height - image_height_end_pixel,
                        image_width_end_pixel + logo_width,
                        image_height - image_height_end_pixel)

            section = im.crop(temp_box)

            if self.verify_compatibility(section, 10):
                print("Logo applied bottom-left!")
            else:
                print("Logo NOT to be applied bottom-left!")
                # top-right box
                box = (image_width - logo_width - image_width_end_pixel,
                       image_height_end_pixel)

                temp_box = (image_width - logo_width - image_width_end_pixel,
                            image_height_end_pixel,
                            image_width - image_width_end_pixel,
                            image_height_end_pixel + logo_height)

                section = im.crop(temp_box)

                if self.verify_compatibility(section, 10):
                    print("Logo applied top-right!")
                else:
                    print("Logo NOT to be applied top-right!")
                    # top-left box
                    box = (image_width_end_pixel,
                           image_height_end_pixel)

                    temp_box = (image_width_end_pixel,
                                image_height_end_pixel,
                                image_width_end_pixel + logo_width,
                                image_height_end_pixel + logo_height)

                    section = im.crop(temp_box)

                    if self.verify_compatibility(section, 10):
                        print("Logo applied top-left!")
                    else:
                        print("Logo NOT to be applied top-left!")

        # load the logo in order to be able to paste it
        self.logo.load()

        # paste the logo over the current image in the "box"
        im.paste(self.logo, box, mask=self.logo.split()[3])

        return im

    def process_images(self):

        if self.images:
            new_dir_path = self.directory + '/Siglator Results'
            try:
                makedirs(new_dir_path, exist_ok=True)
            except:
                print("Error at creating new directory!")

            for image in self.images:
                # open the current image

                im = Image.open(image)

                im = self.paste_logo(im)

                self.progress_bar.step()
                self.progress_bar.update()

                if self.radio_var.get() == 1:
                    im.show()
                elif self.radio_var.get() == 2:
                    print("Salvare poze")
                    photo_path = new_dir_path + "/" + path.split(image)[1]
                    im.save(photo_path)


        else:
            messagebox.showinfo("Info", "No photos found in the selected directory!")

#class MyImage():
 #   def __init__(self):


def main():
    root = tk.Tk()
    app = AppInterface(master=root)
    app.mainloop()

main()

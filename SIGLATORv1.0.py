import tkinter as tk
from tkinter import filedialog
from os import listdir, path, chdir
from PIL import Image, ImageChops
from colorthief import ColorThief
from io import BytesIO

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

    def get_dominant_color(self, image):
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

    def verify_color(self, section_rgb, logo_rgb):
        section_r, section_g, section_b = section_rgb
        logo_r, logo_g, logo_b = logo_rgb

        for index in range(3):
            if(abs(section_rgb[index] - logo_rgb[index]) >= 60):
                return True

        if abs(section_r - section_g) >= 30 and abs(section_r - section_b) >=30:
            return True

        if abs(section_r - section_b) >= 30 and abs(section_r - section_g) >=30:
            return True

        if abs(section_g - section_b) >= 30 and abs(section_g - section_r) >=30:
            return True

        return False

    def process_images(self):

        #open the selected logo
        logo = Image.open(self.logoPath)

        for image in self.images:
            #open the current image
            im = Image.open(image)

            #get and store current image's width and height
            image_width, image_height = im.size[0], im.size[1]

            #set logo's width and height pixel beginning points
            image_width_begin_pixel = int(image_width * 70 / 100)
            image_height_begin_pixel = int(image_height * 70 / 100)

            # set logo's width and height pixel ending points
            image_width_end_pixel = int(image_width * 3 / 100)
            image_height_end_pixel = int(image_height * 3 / 100)


            #size to scale the logo to
            max_logo_size = (image_width - image_width_begin_pixel - image_width_end_pixel, image_height - image_height_begin_pixel - image_height_end_pixel)

            #scale logo
            logo.thumbnail(max_logo_size, Image.ANTIALIAS)

            #get width and height for the scaled logo
            logo_width, logo_height = logo.size[0], logo.size[1]

            #setting the "section" of the image where the logo will be pasted in
            #(starting width pixel, starting height pixel)
            #a.k.a logo's top left corner
            box = (image_width - logo_width - image_width_end_pixel, image_height - logo_height - image_height_end_pixel)

            #santier

            temp_box = (image_width - logo_width - image_width_end_pixel,
                        image_height - logo_height - image_height_end_pixel,
                        image_width - image_width_end_pixel,
                        image_height - image_height_end_pixel )
            section = im.crop(temp_box)

            bytesIO = BytesIO()
            section.save(bytesIO, 'JPEG')
            bytesIO.seek(0)

            #get image section's 4 most frequent colors
            ct = ColorThief(bytesIO)
            #spot_dominant_colors = ct.get_palette(color_count=2)
            spot_dominant_color = ct.get_color(quality=5)
            bytesIO.close()

            #get logo's 4 most frequent colors
            ct2 = ColorThief(self.logoPath)
            #logo_dominant_colors = ct2.get_palette(color_count=2)
            logo_dominant_color = ct2.get_color(quality=5)

            print("Spot dominant color: ", spot_dominant_color)
            #print("Spot secondary colors: ", spot_dominant_colors)
            print("Logo dominant color: ", logo_dominant_color)
            #print("Logo secondary colors: ", logo_dominant_colors)

            if self.verify_color(spot_dominant_color, logo_dominant_color):
                print("Logo is good to be applied bottom-right!")
            else:
                print("NOT a good position for the logo at bottom-right!")

            #section.show()

            #color_thief = ColorThief(self.images[0])
            #print(color_thief.get_color(quality=1))
            #print(color_thief.get_palette(color_count=10))



            #end of santier


            #load the logo in order to be able to paste it
            logo.load()

            #paste the logo over the current image in the "box"
            im.paste(logo, box, mask=logo.split()[3])


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


''' code dump
        #print("Logo width:",logo_width, "Logo height: ", logo_height)
        #print("Future width: ", image_width - logo_width - i_width_out)
        #print("future height: ", image_height - logo_height - i_height_out)
        #box = (image_width - logo_width, image_height - logo_height, image_width, image_height)
        #box = (image_width - logo_width - i_width_out, image_height - logo_height - i_height_out, i_width_out, i_height_out)

        #print("Box width in: ", image_width - logo_width - i_width_out)
        #print("Box height in: ", image_height - logo_height - i_height_out)
        #print("Box width out: ", i_width_out)
        #print("Box height out: ", i_height_out)
        #print("Height size: ", image_height - (image_height - logo_height - i_height_out) - i_height_out)
        #print("Width size: ", image_width - (image_width - logo_width - i_width_out) - i_width_out)
'''
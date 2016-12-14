import multiprocessing
from PIL import Image, ImageTk as ImgTk
from colorthief import ColorThief
from io import BytesIO
from os import makedirs, path


def get_dominant_color(image_reference, quality=10):
    color_thief = ColorThief(image_reference)
    return color_thief.get_color(quality=quality)


def verify_compatibility(section, logo_dominant_color, accuracy=5):
    width, height = section.size
    width_step = int(width / accuracy)

    for i in range(accuracy):

        box = (width_step * i, 0, width_step * (i + 1), height)
        temp_section = section.crop(box)

        bytesIO = BytesIO()
        temp_section.save(bytesIO, 'JPEG')
        bytesIO.seek(0)

        try:
            temp_section_dominant_color = get_dominant_color(bytesIO)
            if not verify_color(temp_section_dominant_color, logo_dominant_color):
                return False
        except:
            return False
        bytesIO.close()
    return True


def verify_color(section_dominant_color, logo_dominant_color):
    section_r, section_g, section_b = section_dominant_color
    print("Logo dom color: ", logo_dominant_color)
    for index in range(3):
        if (abs(section_dominant_color[index] - logo_dominant_color[index]) >= 60):
            return True

    if abs(section_r - section_g) >= 30 and abs(section_r - section_b) >= 30:
        return True

    if abs(section_r - section_b) >= 30 and abs(section_r - section_g) >= 30:
        return True

    if abs(section_g - section_b) >= 30 and abs(section_g - section_r) >= 30:
        return True

    return False


class Photo:
    logo_dominant_color = multiprocessing.Array('i',[0,0,0])
    def __init__(self, image_path, logo_path):
        self.image_path = image_path
        self.image = Image.open(image_path)
        self.logo = Image.open(logo_path)
        self.width, self.height = self.image.size

        #print("New image")

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


def save_image(img, save_directory):
    img.image.save(save_directory + '/' + path.split(img.image_path)[1])


def image_process(image_path, logo_path, save_directory, logo_dominant_color, logo_priority):
    image = Photo(image_path, logo_path)
    for i in logo_priority:
        section = image.logo_pos_index[i]()
        if verify_compatibility(section, logo_dominant_color):
            print("Before apply logo")
            image.apply_logo()
            save_image(image, save_directory)
            print("Image saved!")
            break


def apply_logo(images_paths, logo_path, save_directory):
    try:
        makedirs(save_directory, exist_ok=True)
    except:
        print("Couldn't create the directory!")

    logo_dominant_color = get_dominant_color(logo_path)
    logo_priority = [1, 2, 3, 4]

    arguments = []
    for image_path in images_paths:
        arguments.append((image_path, logo_path, save_directory, logo_dominant_color, logo_priority))

    cpu_count = multiprocessing.cpu_count()

    pool = multiprocessing.Pool(cpu_count)
    pool.starmap(image_process, arguments)


# for cProfile
def test_apply_logo(images_paths, logo_path, save_directory):
    try:
        makedirs(save_directory, exist_ok=True)
    except:
        print("Couldn't create the directory!")

    logo_dominant_color = get_dominant_color(logo_path)
    logo_priority = [1, 2, 3, 4]

    for image_path in images_paths:
        image_process(image_path, logo_path, save_directory, logo_dominant_color, logo_priority)
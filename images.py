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
    # print("Logo dom color: ", logo_dominant_color)
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
    logo_cache = {}

    def __init__(self, image_path, logo_path, offsets, rescale_factor=None):
        self.image_path = image_path
        self.image = Image.open(image_path)

        if rescale_factor:
            self.image.thumbnail(rescale_factor, Image.ANTIALIAS)

        self.width, self.height = self.image.size

        # set logo's scale factor
        self.section_width_scale = int(self.width * offsets[0] / 100)
        self.section_height_scale = int(self.height * offsets[0] / 100)

        # set logo's Horizontal and Vertical offsets
        self.section_horizontal_offset = int(self.width * offsets[1] / 100)
        self.section_vertical_offset = int(self.height * offsets[2] / 100)

        # size to scale the logo to
        logo_scale_box = (self.width - self.section_width_scale,
                          self.height - self.section_height_scale)

        if (self.width, self.height, logo_scale_box) not in Photo.logo_cache:
            print("Not in cache: ", self.width, self.width, logo_scale_box)
            self.logo = Image.open(logo_path)

            # scale logo
            self.logo.thumbnail(logo_scale_box, Image.ANTIALIAS)

            # add to cache
            Photo.logo_cache.update({(self.width, self.height, logo_scale_box): self.logo})
        else:
            print("In cache: ", self.width, self.height, logo_scale_box)
            # retrieve from cache
            self.logo = Photo.logo_cache[(self.width, self.height, logo_scale_box)]

        # scaled logo dimensions
        self.scaled_logo_width, self.scaled_logo_height = self.logo.size

        # dictionary for indexing functions
        self.logo_pos_index = {1: self.get_bottom_right_corner,
                               2: self.get_bottom_left_corner,
                               3: self.get_top_right_corner,
                               4: self.get_top_left_corner}

    def get_image_reference(self):
        return self.image

    def apply_logo(self):
        self.image.paste(self.logo, self.box, mask=self.logo.split()[3])

    def get_bottom_right_corner(self):
        # bottom-right box
        self.box = (self.width - self.scaled_logo_width - self.section_horizontal_offset,
                    self.height - self.scaled_logo_height - self.section_vertical_offset)

        temp_box = (self.width - self.scaled_logo_width - self.section_horizontal_offset,
                    self.height - self.scaled_logo_height - self.section_vertical_offset,
                    self.width - self.section_horizontal_offset,
                    self.height - self.section_vertical_offset)

        section = self.image.crop(temp_box)
        return section

    def get_bottom_left_corner(self):
        # bottom-left box
        self.box = (self.section_horizontal_offset,
                    self.height - self.scaled_logo_height - self.section_vertical_offset)

        temp_box = (self.section_horizontal_offset,
                    self.height - self.scaled_logo_height - self.section_vertical_offset,
                    self.section_horizontal_offset + self.scaled_logo_width,
                    self.height - self.section_vertical_offset)

        section = self.image.crop(temp_box)
        return section

    def get_top_right_corner(self):
        # top-right box
        self.box = (self.width - self.scaled_logo_width - self.section_horizontal_offset,
                    self.section_vertical_offset)

        temp_box = (self.width - self.scaled_logo_width - self.section_horizontal_offset,
                    self.section_vertical_offset,
                    self.width - self.section_horizontal_offset,
                    self.section_vertical_offset + self.scaled_logo_height)

        section = self.image.crop(temp_box)
        return section

    def get_top_left_corner(self):
        # top-left box
        self.box = (self.section_horizontal_offset,
                    self.section_vertical_offset)

        temp_box = (self.section_horizontal_offset,
                    self.section_vertical_offset,
                    self.section_horizontal_offset + self.scaled_logo_width,
                    self.section_vertical_offset + self.scaled_logo_height)

        section = self.image.crop(temp_box)
        return section


def save_image(img, save_directory):
    img.image.save(save_directory + '/' + path.split(img.image_path)[1])


def image_process(image_path, logo_path, save_directory, logo_dominant_color, logo_priority, offsets):
    image = Photo(image_path, logo_path, offsets)
    for i in logo_priority:
        section = image.logo_pos_index[i]()
        if verify_compatibility(section, logo_dominant_color):
            image.apply_logo()
            save_image(image, save_directory)
            break


def preview_images(images_paths, logo_path, logo_priority, current_photo_index, offsets):
    try:
        # get the photo to the path that will be displayed
        image_path = images_paths[current_photo_index]
        logo_dominant_color = get_dominant_color(logo_path)

        image = Photo(image_path, logo_path, offsets, (960, 540))
        for i in logo_priority:
            section = image.logo_pos_index[i]()
            if verify_compatibility(section, logo_dominant_color):
                image.apply_logo()
                break
        return image.get_image_reference()
    except:
        print("Can't preview photo")


def apply_logo(images_paths, logo_path, save_directory, logo_priority, offsets):
    try:
        makedirs(save_directory, exist_ok=True)
    except:
        print("Couldn't create the directory!")

    logo_dominant_color = get_dominant_color(logo_path)
    arguments = []
    for image_path in images_paths:
        arguments.append((image_path, logo_path, save_directory,
                          logo_dominant_color, logo_priority, offsets))

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

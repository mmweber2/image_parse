import cv2
from PIL import Image
import numpy

# TODO: The current process is to find the blanks, crop the blanks which are
#     borders, then find the center blanks again, since they will have moved.
#     This should be made more efficient.
# TODO: Error checking

def threshold(filepath):
    """Converts an image to black on white."""
    img = cv2.imread(filepath, 0)
    ret, thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    # First pixel is very likely to be the background color
    if thresh[0][0] < ret:
        # If background is darker than foreground, invert black/white
        thresh = cv2.bitwise_not(thresh)
    return thresh

# TODO: Find a way to combine these two functions
def find_vert_ranges(pixels, size):
    """Identifies vertical ranges (splits) of blank (255) pixels."""
    x, y = size
    blanks = []
    for line in xrange(y):
        for pixel in xrange(x):
            if pixels[line][pixel] != 255:
            # Found non-background pixel; row/column is not blank
                break
        else:
            blanks.append(line)
    return blanks

def find_horiz_ranges(pixels, size):
    """Identifies horizontal ranges (splits) of blank (255) pixels."""
    x, y = size
    blanks = []
    for line in xrange(x):
        for pixel in xrange(y):
            if pixels[pixel][line] != 255:
            # Found non-background pixel; row/column is not blank
                break
        else:
            blanks.append(line)
    return blanks

# TODO: Find a better way to pass the blanks
def crop_border(image, vert_blanks, horiz_blanks):
    """Returns a copy of an image with its blank borders removed."""
    if not (vert_blanks or horiz_blanks):
        return image.copy()
    border = [] # Left, upper, right, lower
    for section in vert_blanks:
        if section[0] == 0:
            border.append(section[1])
        elif section[1] == image.size[1] - 1:
            border.append(section[0])
    for section in horiz_blanks:
        if section[0] == 0:
            border.append(section[1])
        elif section[1] == image.size[0] - 1:
            border.append(section[0])
    # Since we processed the vertical blanks first, our order will be
    #     upper, lower, left, right.
    # PIL's crop requires a tuple of (left, upper, right, lower).
    box = (border[2], border[0], border[3], border[1])
    cropped = image.crop(box)
    # Call load to ensure original image is left intact
    cropped.load()
    return cropped

# Size is only in the relevant dimension
def get_split_ranges(blanks, size):
    """Given locations of blank pixels, finds their boundaries."""
    # TODO: Should this raise an error?
    if not blanks:
        return []
    ranges = []
    start = blanks[0]
    end = blanks[0]
    for loc in blanks[1:]:
        if (loc != end + 1):
            ranges.append((start, end))
            # New range encountered, so reset start
            start = loc
        # End always moves regardless of whether a match was found
        end = loc
    if start != end:
        # A blank range reaches the end of the image
        ranges.append((start, end))
    return ranges

img = Image.open("kizoku_bw.png")
h_blanks = find_horiz_ranges(numpy.asarray(img), img.size)
v_blanks = find_vert_ranges(numpy.asarray(img), img.size)
h_ranges = get_split_ranges(h_blanks, img.size[1])
v_ranges = get_split_ranges(v_blanks, img.size[0])
cropped = crop_border(img, v_ranges, h_ranges)
cropped.show()

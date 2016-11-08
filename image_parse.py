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

def find_ranges(pixels, size, dimension):
    """Identifies ranges (splits) of blank (255) pixels."""
    # If dimension is y, looks for empty rows (splits on y axis).
    # If dimension is x, looks for empty columns (splits on x axis).
    if dimension == "x":
        dim1, dim2 = size
    elif dimension == "y":
        dim2, dim1 = size
    else:
        raise ValueError("dimension must be one of strings x, y")
    blanks = []
    for line in xrange(dim1):
        for pixel in xrange(dim2):
            if dimension == "y":
                if pixels[line][pixel] != 255:
                    # Found non-background pixel; row is not blank
                    break
            elif dimension == "x":
                if pixels[pixel][line] != 255:
                    # Found non-background pixel; column is not blank
                    break
        else:
            blanks.append(line)
    return blanks

# TODO: Find a better way to pass the blanks
def crop_border(image, vert_blanks, horiz_blanks):
    """Returns a copy of an image with its blank borders removed."""
    if not (vert_blanks or horiz_blanks):
        return image.copy()
    border = []
    # Check for top, bottom, left, and right borders
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

# TODO: Find a better way to get the blanks than passing them around.
#        Maybe make a class for the image and store these values as attributes.
def find_character_size(pixels, vert_blanks, horiz_blanks):
    """Given a cropped image array, returns the estimated character size."""
    if pixels[0][0] == 255:
        raise ValueError(
                "Image must be border cropped before checking character size")
    # Look for the first vertical and horizontal line that meet from 0, 0
    # TODO: Get the line breaks and return (x, y) of their lower right corner



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
empty_rows = find_ranges(numpy.asarray(img), img.size, "y")
empty_cols = find_ranges(numpy.asarray(img), img.size, "x")
blank_y_ranges = get_split_ranges(empty_rows, img.size[1])
blank_x_ranges = get_split_ranges(empty_cols, img.size[0])
cropped = crop_border(img, blank_y_ranges, blank_x_ranges)
cropped.show()

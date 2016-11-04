import cv2
from PIL import Image
import numpy

def threshold(filepath):
    """Converts an image to black on white."""
    img = cv2.imread(filepath, 0)
    ret, thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    # First pixel is very likely to be the background color
    if thresh[0][0] < ret:
        # If background is darker than foreground, invert black/white
        thresh = cv2.bitwise_not(thresh)
    return thresh

def find_blank_horizontal_ranges(pixels, size):
    """Identifies horizontal ranges (vertical splits) of blank (255) pixels."""
    x, y = size
    blanks = []
    for line in xrange(y):
        for pixel in xrange(x):
            if pixels[line][pixel] != 255:
            # Found non-background pixel
                break
        else:
            blanks.append(line)
    return blanks

# Size is only in the relevant dimension
def get_split_ranges(blanks, size):
    """Given locations of blank pixels, finds their boundaries."""
    # TODO: Should this raise an error?
    if not blanks:
        return []
    ranges = []
    print blanks
    start = blanks[0]
    end = blanks[0]
    for loc in blanks[1:]:
        if loc != end + 1:
            if start == 0 or end == size - 1:
                # Don't consider blanks at the top, bottom, left, or right
                # Reset start and end for next range
                start = loc
                end = loc
                continue
            ranges.append((start, end))
            # New range encountered, so reset start
            start = loc
        # End always moves regardless of whether a match was found
        end = loc
    return ranges

img = Image.open("kizoku_bw.png")
blanks = find_blank_horizontal_ranges(numpy.asarray(img), img.size)
get_split_ranges(blanks, img.size[1])

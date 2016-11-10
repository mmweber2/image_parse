import cv2
from PIL import Image
from matplotlib import pyplot as plt
import numpy

# TODO: The current process is to find the blanks, crop the blanks which are
#     borders, then find the center blanks again, since they will have moved.
#     This should be made more efficient.
# TODO: Error checking

class TextImage(object):
    """Represents an image containing text characters."""
    image = None
    empty_rows = None
    empty_cols = None
    height = None
    width = None

    def __init__(self, filepath):
        """Reads in an image as black and white."""
        self.image = cv2.imread(filepath, 0)
        # Empty rows/columns are not yet identified
        self.empty_rows = []
        self.empty_cols = []
        # shape is in the format (height, width, color_channels)
        self.height = self.image.shape[0]
        self.width = self.image.shape[1]

    def threshold(self):
        """Converts image to black on white."""
        # CV2 settings for thresholding
        thresh_settings = cv2.THRESH_BINARY+cv2.THRESH_OTSU
        ret, thresh = cv2.threshold(self.image, 0, 255, thresh_settings)
        # First pixel is very likely to be the background color
        if thresh[0][0] < ret:
            # If background is darker than foreground, invert black/white
            thresh = cv2.bitwise_not(thresh)
        self.image = thresh

    def find_ranges(self):
        """Identifies ranges (splits) of blank (255) pixels."""
        pixels = numpy.asarray(self.image)
        x, y = self.width, self.height
        empty_rows = []
        for row in xrange(y):
            for col in xrange(x):
                if pixels[row][col] != 255:
                    # Found non-background pixel; row is not blank
                    break
            else:
                empty_rows.append(row)
        empty_cols = []
        for col in xrange(x):
            for row in xrange(y):
                if pixels[row][col] != 255:
                    # Found non-background pixel; column is not blank
                    break
            else:
                empty_cols.append(col)
        # Convert row/column numbers into ranges before assigning
        self.empty_rows = get_split_ranges(empty_rows)
        self.empty_cols = get_split_ranges(empty_cols)

    def crop_border(self):
        """Removes blank borders from the image."""
        if not (self.empty_rows or self.empty_cols):
            raise ValueError("No blank ranges found; run find_ranges first.")
        # If no blank borders are found, cropping means keeping the full image
        x1, y1 = 0, 0
        x2 = self.width
        y2 = self.height
        # Check for top, bottom, left, and right borders
        for section in self.empty_rows:
            if section[0] == 0:
                y1 = section[1]
            elif section[1] == self.height - 1:
                y2 = section[0]
        for section in self.empty_cols:
            if section[0] == 0:
                x1 = section[1]
            elif section[1] == self.width - 1:
                x2 = section[0]
        # Crop by slicing the numpy array
        self.image = self.image[y1:y2, x1:x2]
        # Adjust blank rows/columns by top and left borders and update sizes
        y_diff = y1
        self.empty_rows = [(s-y_diff, e-y_diff) for s, e in self.empty_rows[1:]]
        self.height =- y_diff
        x_diff = x1
        self.empty_cols = [(s-x_diff, e-x_diff) for s, e in self.empty_cols[1:]]
        self.width -= x_diff

    # TODO: Before doing this, we need to split text into rows
    #       Then, look for horizontal splits between characters
    def find_character_size(self):
        """Given a cropped image array, returns the estimated character size."""
        if pixels[0][0] == 255:
            raise ValueError("Image must be border cropped first")
        rows = self.get_text_rows()
        # TODO: Start here

def get_text_rows(image):
    """Splits a TextImage into a list of TextImages based on vertical spaces."""
    text_lines = []
    previous = 0
    for row in self.empty_rows:
            # TODO: Crop extra horizontal space from shorter rows
            # TODO: Make new TextImage objects out of these
            text_lines.append(self.image[previous:row[0], 0:self.width])
            # Start from the next non-blank row
            previous = row[1]
        return text_lines

def get_split_ranges(blanks):
    """Given lists of integers, condense them into ranges."""
    if not blanks:
        return []
    ranges = []
    start = blanks[0]
    end = blanks[0]
    for pos in blanks[1:]:
        if (pos != end + 1):
            ranges.append((start, end))
            # New range encountered, so reset start
            start = pos
        # End always moves regardless of whether a match was found
        end = pos
    if start != end:
        # The last range contained at least one blank
        ranges.append((start, end))
    return ranges

img = TextImage("kizoku_bw.png")
img.threshold()
img.find_ranges()
img.crop_border()
rows = img.get_text_rows()
for row in rows:
    plt.imshow(row)
    plt.show()
# imshow is not working on my installation
#cv2.imshow("Text", img.image)

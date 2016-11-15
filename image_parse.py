import cv2
from PIL import Image
from matplotlib import pyplot as plt
import numpy

# TODO: Error checking

class TextImage(object):
    """Represents an image containing text characters."""
    image = None
    empty_rows = None
    empty_cols = None
    height = None
    width = None

    def __init__(self, filepath=None, array=None):
        """Creates a new TextImage from a file or numpy array."""
        # Check filepath first, and read in an image as black and white
        if filepath:
            self.image = cv2.imread(filepath, 0)
        elif array is not None:
            self.image = array
        else:
            # Make a blank, empty image
            self.image = numpy.zeros((0), numpy.uint8)
        # Empty rows/columns are not yet identified
        self.empty_rows = []
        self.empty_cols = []
        # shape is in the format (height, width, color_channels)
        self.height = self.image.shape[0]
        self.width = self.image.shape[1]
        self.threshold()
        self._set_ranges()

    def threshold(self):
        """Converts image to black on white."""
        # CV2 settings for Otsu's binary thresholding
        thresh_settings = cv2.THRESH_BINARY+cv2.THRESH_OTSU
        # threshold returns the Otsu threshold value and threshed image array
        t_value, t_image = cv2.threshold(self.image, 0, 255, thresh_settings)
        # First pixel is very likely to be the background color
        if t_image[0][0] < t_value:
            # If background is darker than foreground, invert black/white
            t_image = cv2.bitwise_not(t_image)
        self.image = t_image

    def _set_ranges(self):
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
            raise ValueError("No blank ranges found")
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
        self.empty_rows = [(s - y1, e - y1) for s, e in self.empty_rows[1:]]
        self.height =- y1
        self.empty_cols = [(s - x1, e - x1) for s, e in self.empty_cols[1:]]
        self.width -= x1

    # TODO: Before doing this, we need to split text into rows
    #       Then, look for horizontal splits between characters
    def find_character_size(self):
        """Given a cropped image array, returns the estimated character size."""
        # TODO: Start here
        rows = get_text_rows(self)
        chars = []
        for row in rows:
            size = row.height
            print "Estimated size: ", size
            x_pos = 0
            while x_pos < row.width:
                char = TextImage(array=row.image[0:size, x_pos:x_pos + size])
                # Median value; TODO
                x_pos += 3 + size
                chars.append(char)
        for char in chars:
            plt.imshow(char.image)
            plt.show()
#for row in rows:
    #plt.imshow(row.image)
    #plt.show()

def get_text_rows(img):
    """Splits a TextImage into a list of TextImages based on vertical spaces."""
    text_lines = []
    previous = 0
    for row in img.empty_rows:
        # TODO: Crop extra horizontal space from shorter rows
        row_img = TextImage(array=img.image[previous:row[0], 0:img.width])
        print "Row has empty cols ", row_img.empty_cols
        # TODO: This is just temporary experimentation
        # Median horizontal spacing in this row
        widths = sorted(end - start for start, end in row_img.empty_cols)
        median = widths[len(widths)/2]
        print "Median spacing is ", median
        text_lines.append(row_img)
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

img = TextImage(filepath="kizoku_bw.png")
img.crop_border()
#plt.imshow(img.image)
#plt.show()
img.find_character_size()
# imshow is not working on my installation
#cv2.imshow("Text", img.image)

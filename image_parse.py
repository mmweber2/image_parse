#!/usr/local/bin/python
# coding: utf-8

import cv2
from PIL import Image
from matplotlib import pyplot as plt
import numpy
from bisect import bisect_left

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

    # TODO: What happens if the whole image is blank?
    def crop_border(self, vertical=True):
        """Removes blank borders from the image."""
        # If vertical is False, don't crop on y axis
        if not (self.empty_rows or self.empty_cols):
            raise ValueError("No blank ranges found")
        # If no blank borders are found, cropping means keeping the full image
        x1, y1 = 0, 0
        x2 = self.width
        y2 = self.height
        # Check for top, bottom, left, and right borders
        if vertical:
            for section in self.empty_rows:
                if section[0] == 0:
                    # Leave an extra pixel on each side
                    y1 = max(0, section[1] - 1)
                elif section[1] == self.height - 1:
                    y2 = section[0] + 1
        for section in self.empty_cols:
            if section[0] == 0:
                x1 = max(0, section[1] - 1)
            elif section[1] == self.width - 1:
                x2 = section[0] + 1
        # Crop by slicing the numpy array
        self.image = self.image[y1:y2, x1:x2]
        # Adjust blank rows/columns by top and left borders and update sizes
        self.empty_rows = [(s - y1, e - y1) for s, e in self.empty_rows[1:]]
        self.height = y2 - y1
        c = [(s - x1, e - x1) for s, e in self.empty_cols[1:] if e <= x2 - x1]
        self.empty_cols = c
        self.width = x2 - x1

    # TODO: Change to split_characters
    def find_character_size(self):
        """Given a cropped image array, returns the estimated character size."""
        # TODO: For now, just calling this for testing
        for row in get_text_rows(self):
            TextImage.split_characters(row)
        return 0

    @staticmethod
    def split_characters(row):
        """Given a TextImage row, split it into character TextImages."""
        chars = [row]
        widths = sorted(e - s for s, e in row.empty_cols if s != e)
        # Median horizontal spacing in this row
        space_size = widths[len(widths)/2] - 1
        # Get columns that are large enough to be full spaces
        spaces = [(x, y) for x, y in row.empty_cols if y >= (x + space_size)]
        space_index = 0
        previous_x = 0
        print "Width is ", row.width
        print "The empty cols are ", row.empty_cols
        while True:
            c_start = previous_x
            last_char = False
            if space_index >= len(spaces):
                # If this is the last character, it should reach the end of row
                c_end = row.width
                print "Found last char"
                last_char = True
            else:
                c_end = spaces[space_index][0] + 2
            if c_end - c_start <= row.height + 2:
                # Small or normal sized character
                if not last_char:
                    previous_x = spaces[space_index][1] - 1
                    print "This space is ", spaces[space_index]
                    print "Previous x is now ", previous_x
                space_index += 1
            else:
                print "It's too big!"
                print c_end - c_start
                # Too big to be a single character; split in half
                # Find maximum gap within this range
                midpoint = 0
                max_gap = 0
                for gap in row.empty_cols:
                    # Gap occurs after this character
                    if gap[0] > c_end:
                        print "Breaking, gap is after ", c_end
                        break
                    if c_start <= gap[0] and gap[1]  <= c_end:
                        if gap[1] - gap[0] > max_gap:
                            max_gap = gap[1] - gap[0]
                            midpoint = (gap[1] + gap[0]) / 2
                previous_x = midpoint
                c_end = midpoint
            print "Making character from {} to {}".format(c_start, c_end)
            char = TextImage(array=row.image[0:row.height, c_start:c_end])
            chars.append(char)
            if last_char:
                break
        # Testing section
        for char in chars:
            plt.imshow(char.image)
            plt.show()

def get_text_rows(img):
    """Splits a TextImage into a list of TextImages based on vertical spaces."""
    text_lines = []
    previous = 0
    for row in img.empty_rows:
        # row is a tuple of (blank_row_start, blank_row_end)
        row_img = TextImage(array=img.image[previous:row[0] + 1, 0:img.width])
        # Remove extra horizontal (x axis) space from each row
        row_img.crop_border(vertical=False)
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

img = TextImage(filepath="sphere_bw.png")
img.crop_border()
#plt.imshow(img.image)
#plt.show()
img.find_character_size()
# imshow is not working on my installation
#cv2.imshow("Text", img.image)

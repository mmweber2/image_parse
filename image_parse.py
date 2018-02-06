#!/usr/local/bin/python
# coding: utf-8

import cv2
from PIL import Image
from matplotlib import pyplot as plt
from collections import Counter
import numpy

# TODO: Error checking

class TextImage(object):
    """Represents an image containing text characters."""
    image = None
    empty_rows = []
    empty_cols = []
    height = None
    width = None

    def __init__(self, filepath=None, array=None):
        """Creates a new TextImage from a file or numpy array.
        
        If filepath is specified, reads in the image from filepath.
        If filepath is not specified and if array is, reads in the given array.
        Otherwise, creates a new, empty array.
        
        Args:
            filepath: String, the relative or absolute path of the image file
                to read in. If not provided, array will be checked instead.

            array: a 2D list corresponding to a numpy image array.
                This parameter is only checked if filepath is None.
                If filepath and array are both None, a blank image is created.
                Defaults to None.
        """
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
        """Converts this TextImage to black on white using Otsu's method."""
        # CV2 settings for Otsu's binary thresholding
        thresh_settings = cv2.THRESH_BINARY+cv2.THRESH_OTSU
        # threshold returns the Otsu threshold value and threshed image array
        t_value, t_img = cv2.threshold(self.image, 0, 255, thresh_settings)
        # Check four corners of image; the most common color there is likely
        # to be the background color
        corners = (t_img[0][0], t_img[-1][-1], t_img[0][-1], t_img[-1][0])
        # Get the most common corner pixel (any if tied)
        if Counter(corners).most_common(1)[0][0] < t_value:
            # If background is darker than foreground, invert black/white
            t_img = cv2.bitwise_not(t_img)
        self.image = t_img

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
        # The above just notes the individual empty rows and columns,
        # so convert those numbers into ranges before assigning
        self.empty_rows = get_split_ranges(empty_rows)
        self.empty_cols = get_split_ranges(empty_cols)

    # TODO: What happens if the whole image is blank?
    # TODO: Document what if there is no cropping to do
    # Argument is "full_image" for disambiguation from TextImage.image
    @staticmethod
    def crop_border(full_image, crop_vertical=True):
        """Removes blank borders from the image.
        
        Args:
            full_image: TextImage, the image to crop.

            crop_vertical: boolean, whether or not to crop on the y-axis.
                If set to False, this method can be used to trim empty space
                from the left and right borders, while leaving vertical spacing
                intact.
                Defaults to True.

     Raises:
            ValueError: empty_rows and empty_cols are both empty for this image.
                This results from incorrect initialization of the TextImage.
        """
        # If no blank borders are found, keep the full image
        x1, y1 = 0, 0
        x2 = full_image.width
        y2 = full_image.height
        # Check for top, bottom, left, and right borders
        if crop_vertical:
            for start, stop in full_image.empty_rows:
                if start == 0:
                    # Leave an extra pixel on each side for visibility
                    y1 = max(0, stop - 1)
                elif stop == full_image.height - 1:
                    y2 = start + 1
        for start, stop in full_image.empty_cols:
            if start == 0:
                x1 = max(0, stop - 1)
            elif stop == full_image.width - 1:
                x2 = start + 1
        # Crop by slicing the numpy array
        full_image.image = full_image.image[y1:y2, x1:x2]
        # Adjust blank rows/columns by top and left borders and update sizes
        # First blank section will be cropped out, so remove it from the list
        full_image.empty_rows = [(s - y1, e - y1) for s, e in full_image.empty_rows[1:]]
        full_image.height = y2 - y1
        # Filter out any range ends that are beyond the new size
        c = [(s - x1, e - x1) for s, e in full_image.empty_cols[1:] if e <= x2 - x1]
        full_image.empty_cols = c
        full_image.width = x2 - x1

    @staticmethod
    def split_characters(row):
        """Given a TextImage row, split it into character TextImages.
        
        Args:
            row: TextImage, a single row of text to split into single
                characters.
                Use get_text_rows to split an image into these rows.
                
        Returns:
            A list of TextImage objects of each character in row in the
                same order.
        """
        chrs = []
        widths = sorted(e - s for s, e in row.empty_cols if s != e)
        # Median horizontal spacing in this row
        space_size = widths[len(widths)/2] - 1
        # Get columns that are large enough to be full spaces
        spaces = [(x, y) for x, y in row.empty_cols if y >= (x + space_size)]
        space_index = 0
        previous_x = 0
        while True:
            # Characters added this iteration
            new_chrs = []
            c_start = previous_x
            # Is this the last character in the row?
            last_char = False
            if space_index >= len(spaces) or c_start >= row.width:
                # If this is the last character, it should reach the end of row
                c_end = row.width
                last_char = True
            else:
                # Pad with extra pixels for clarity
                c_end = spaces[space_index][0] + 2
            if c_end - c_start <= row.height + 2:
                # Small or normal sized character
                new_chrs.append(row.image[0:row.height, c_start:c_end])
                if not last_char:
                    previous_x = spaces[space_index][1] - 1
                space_index += 1
            else:
                # Too big to be a single character; split into pieces
                while c_end - c_start > row.height + 2:
                    # Still too big; try splitting
                    gap = TextImage._find_split(c_start, c_end, row.empty_cols)
                    previous_x = gap
                    c_end = gap
                    if c_end - c_start <= row.height + 2:
                        new_chrs.append(row.image[0:row.height, c_start:c_end])
            chrs.extend(TextImage(array=character) for character in new_chrs)
            if last_char:
                break
        return chrs

    @staticmethod
    def _find_split(chr_start, chr_end, cols):
        """Returns the location of the largest gap within a character."""
        # Given start and end indices and a series of blank columns, finds
        #    the largest split between those indices and returns the middle
        #    of that split.
        midpoint = 0
        max_gap = 0
        for gap_start, gap_end in cols:
            # Gap occurs after this character; stop looking
            if gap_start > chr_end:
                return midpoint
            if chr_start < gap_start and gap_end < chr_end:
                # Gap divides this character
                if gap_end - gap_start >= max_gap:
                    max_gap = gap_end - gap_start
                    midpoint = (gap_start + gap_end) / 2
        return midpoint

def get_text_rows(img):
    """Splits a TextImage into a list of TextImages based on vertical spaces."""
    text_lines = []
    previous = 0
    for row in img.empty_rows:
        # row is a tuple of (blank_row_start, blank_row_end)
        row_img = TextImage(array=img.image[previous:row[0] + 1, 0:img.width])
        # Remove extra horizontal (x axis) space from each row
        # Don't crop vertically, leave some vertical padding intact
        row_img.crop_border(crop_vertical=False)
        text_lines.append(row_img)
        # Start from the next non-blank row
        previous = row[1]
    return text_lines

def get_split_ranges(array):
    """Given a list of integers, condense the numbers into ranges.
    
    Args:
        array: list of distinct integers. In order to find all consecutive
            number ranges, array must be in sorted order.

            If array contains duplicate values, the ranges will start and end
            on those values rather than including them and continuing.
        
    Returns:
        A list of two-tuples containing integers indicating the start and end
            (inclusive) of each consecutive range. If an integer is not part of
            a consecutive sequence, it will be added as both a start and end
            value.

        For example, if array is [1, 2, 3, 6, 7, 8, 10], the return value
            would be [(1, 3), (6, 8), (10, 10)].
        """
    if not array:
        return []
    ranges = []
    start = array[0]
    end = array[0]
    for pos in array[1:]:
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

# Usage: set path to relative or absolute filepath
path = "Sophie.png"
img = TextImage(filepath=path)
img.crop_border()
plt.imshow(img.image)
plt.show()
chars = []
for row in get_text_rows(img):
    chars.extend(TextImage.split_characters(row))
# Testing section
for char in chars[13:20]:
    plt.imshow(char.image)
    plt.show()

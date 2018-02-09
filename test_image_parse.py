import image_parse
import mock
import numpy
import cv2
from StringIO import StringIO
from nose.tools import assert_raises
from nose.tools import assert_less
from nose.tools import assert_not_equal

def test_constructor_empty():
    test = image_parse.TextImage()
    # The image array should be full of 255s (blank pixels)
    assert all(test.image)
    # Even a blank image should have width and height
    assert test.height
    assert test.width

@mock.patch('cv2.imread', return_value=None)
def test_constructor_filepath_invalid(mock_test):
    path = "./None.png"
    assert_raises(ValueError, image_parse.TextImage, path)

def test_constructor_filepath_valid_image():
    path = "./screenshots/utsubo_bw.png"
    img = image_parse.TextImage(path)
    assert img is not None
    assert len(img.image)

def test_constructor_filepath_bw_inverted_image():
    path = "./screenshots/utsubo_bw2.png"
    img = image_parse.TextImage(path)
    assert img is not None
    assert len(img.image)

def test_constructor_filepath_non_image():
    path = "./screenshots/cat.txt"
    assert_raises(ValueError, image_parse.TextImage, path)

def test_crop_border_no_space_vertical_true():
    path = "./screenshots/utsubo_bw.png"
    img = image_parse.TextImage(path)
    orig_height, orig_width = img.height, img.width
    orig_rows, orig_cols = img.empty_rows, img.empty_cols
    image_parse.TextImage.crop_border(img)
    # The specific values may change, but for this image, it should
    #   be cropped both horizontally and vertically, changing the size
    #   and removing some of the empty spaces.
    assert_less(img.height, orig_height)
    assert_less(img.width, orig_width)
    assert_not_equal(img.empty_rows, orig_rows)
    assert_not_equal(img.empty_cols, orig_cols)

# TODO:
#   Crop with vertical=False
#   Crop when already cropped
#   Crop empty image
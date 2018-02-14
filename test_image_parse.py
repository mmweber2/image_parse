import image_parse
import mock
import numpy
import cv2
from StringIO import StringIO
from nose.tools import assert_raises
from nose.tools import assert_less
from nose.tools import assert_not_equal
from nose.tools import assert_equals

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

def test_crop_border_no_space_vertical_false():
    path = "./screenshots/utsubo_bw.png"
    img = image_parse.TextImage(path)
    orig_height, orig_width = img.height, img.width
    orig_rows, orig_cols = img.empty_rows, img.empty_cols
    image_parse.TextImage.crop_border(img, crop_vertical=False)
    # Vertical values should be unchanged
    assert_equals(img.height, orig_height)
    assert_equals(img.empty_rows, orig_rows)
    # Horizontal values should be changed
    assert_less(img.width, orig_width)
    assert_not_equal(img.empty_cols, orig_cols)
    #cv2.imwrite("./screenshots/crop_test.png", img.image)

def test_crop_border_already_cropped():
    path = "./screenshots/utsubo_bw_cropped.png"
    img = image_parse.TextImage(path)
    orig_height, orig_width = img.height, img.width
    orig_rows, orig_cols = img.empty_rows, img.empty_cols
    image_parse.TextImage.crop_border(img)
    # A cropped image shouldn't be cropped further
    assert_equals(img.height, orig_height)
    assert_equals(img.width, orig_width)
    assert_equals(img.empty_rows, orig_rows)
    assert_equals(img.empty_cols, orig_cols)

def test_crop_border_blank_image():
    path = "./screenshots/blank_image.png"
    img = image_parse.TextImage(path)
    orig_height, orig_width = img.height, img.width
    orig_rows, orig_cols = img.empty_rows, img.empty_cols
    image_parse.TextImage.crop_border(img)
    # A blank image doesn't have anything to crop
    assert_equals(img.height, orig_height)
    assert_equals(img.width, orig_width)
    assert_equals(img.empty_rows, orig_rows)
    assert_equals(img.empty_cols, orig_cols)

def test_split_row_valid_row():
    path = "./screenshots/utsubo_bw_cropped.png"
    img = image_parse.TextImage(path)
    result = image_parse.TextImage.split_row(img)
    assert len(result) > 1

def test_split_row_not_a_row():
    path = "./screenshots/123816.jpg"
    img = image_parse.TextImage(path)
    # Should return some images, but they are probably not characters
    assert image_parse.TextImage.split_row(img)

def test_split_row_blank_image():
    path = "./screenshots/blank_image.png"
    img = image_parse.TextImage(path)
    assert_raises(IndexError, image_parse.TextImage.split_row, img)

def test_split_row_single_character():
    path = "./screenshots/temp_chr.jpg"
    img = image_parse.TextImage(path)
    assert image_parse.TextImage.split_row(img)

def test_split_row_not_textimage():
    assert_raises(AttributeError, image_parse.TextImage.split_row, "")

# _find_split input format: area start, area end, columns (start,end tuples)
def test_find_split_single_split():
    assert_equals(0, image_parse.TextImage._find_split(0, 100, [(120, 150)]))

def test_find_split_multiple_tied_splits():
    assert_equals(0, image_parse.TextImage._find_split(0, 200, [(50, 100), (100, 150)]))

def test_find_split_multiple_different_sizes():
    pass

def test_find_split_against_range_start():
    pass

def test_find_split_against_range_end():
    pass

def test_find_split_against_range_end_and_start():
    pass

def test_find_split_no_splits():
    assert_equals(0, image_parse.TextImage._find_split(0, 100, []))

def test_find_split_none_in_range():
    assert_equals(0, image_parse.TextImage._find_split(0, 100, [(120, 150)]))


# TODO: Add tests for threshold; it breaks when used on an image made from [].
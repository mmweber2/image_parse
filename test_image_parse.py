import image_parse
import mock
import numpy
from StringIO import StringIO
from nose.tools import assert_raises

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
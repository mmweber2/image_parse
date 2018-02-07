import image_parse
import mock
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
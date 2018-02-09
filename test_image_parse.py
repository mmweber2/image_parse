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

sample_array = [[105, 105, 103, 105, 103, 105],
                [105, 106, 107, 109, 109, 107],
                [107, 107, 107, 109, 110, 107],
                [107, 107, 105, 107, 109, 105],
                [107, 109, 112, 112, 110, 107],
                [111, 111, 110, 111,  93, 118]]

sample_array2 = [[255, 255, 255, 255, 255, 255],
                [255, 255, 255, 0, 0, 255],
                [255, 255, 255, 0, 0, 255],
                [255, 255, 255, 255, 0, 255],
                [255, 0, 0, 0, 0, 255],
                [0, 0, 0, 0, 255, 0]]

sample_np_array = numpy.array(sample_array2)
import image_parse

def test_constructor_empty():
    test = image_parse.TextImage()
    # The image array should be full of 255s (blank pixels)
    assert all(test.image)
    # Even a blank image should have width and height
    assert test.height
    assert test.width
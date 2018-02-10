# image_parse

This program is for tokenizing images that contain text into a set of
    smaller, more manageable character images.

# TODO: Usage will change when more finished
From image_parse.py, create a TextImage either by providing a filepath or
    from a blank file.

Once initialized, you can perform the following actions on a TextImage:

crop_border: Remove non-text boundary from the edges.
get_text_rows: Split a TextImage with multiple text rows into multiple single-row TextImages.
split_characters: Split a row (from get_text_rows) into single character TextImages.

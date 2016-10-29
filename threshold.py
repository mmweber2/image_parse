from PIL import Image
from skimage import io
io.use_plugin('pil')
io.use_plugin('matplotlib')
from skimage import filters
import matplotlib.pyplot as plt
import numpy

def bw_convert(filepath):
    # Given a color image, converts to black and white and saves.
    img = Image.open(filepath)
    bw_img = img.convert("L", dither=None)
    bw_img.save(filepath + "_bw.png", "PNG")

#bw_convert("/Users/Toz/code/image_parse/Screenshots/UtsuboScreen.png")


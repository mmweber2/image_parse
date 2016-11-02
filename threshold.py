from PIL import Image
import cv2
import matplotlib.pyplot as plt
import numpy

def threshold(filepath):
    img = cv2.imread(filepath, 0)
    ret, thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    #plt.imshow(cv2.cvtColor(thresh, cv2.COLOR_BGR2RGB))
    #plt.show()
    cv2.imwrite('utsubo_bw.png', thresh)
    
threshold("/Users/Toz/code/image_parse/Screenshots/UtsuboScreen.png")


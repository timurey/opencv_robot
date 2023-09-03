import cv2
import numpy as np

def image_resize(image, width = None, height = None, inter = cv2.INTER_AREA):
    # initialize the dimensions of the image to be resized and
    # grab the image size
    dim = None
    (h, w) = image.shape[:2]

    # if both the width and height are None, then return the
    # original image
    if width is None and height is None:
        return image

    # check to see if the width is None
    if width is None:
        # calculate the ratio of the height and construct the
        # dimensions
        r = height / float(h)
        dim = (int(w * r), height)

    # otherwise, the height is None
    else:
        # calculate the ratio of the width and construct the
        # dimensions
        r = width / float(w)
        dim = (width, int(h * r))

    # resize the image
    resized = cv2.resize(image, dim, interpolation = inter)

    # return the resized image
    return resized


def doCardBoardImage(frameLeft, frameRight, width, height):

    sizesL = frameLeft.shape[:2]
    sizesR = frameRight.shape[:2]
    ratioL = sizesL[1]/sizesL[0]
    ratioR = sizesR[1]/sizesR[0]
    newRatio = (width/2)/height

    if (newRatio<ratioL):
        newHeightL = sizesL[0]
        newWidthL = int(newHeightL * newRatio)
    else:
        newWidthL = sizesL[1]
        newHeightL = int(newWidthL / newRatio)

    if (newRatio<ratioR):
        newHeightR = sizesR[0]
        newWidthR = int(newHeightR * newRatio)
    else:
        newWidthR = sizesR[1]
        newHeightR = int(newWidthR / newRatio)

    croppedLeft = frameLeft[0:newHeightL, int((sizesL[1]-newWidthL)/2):int((sizesL[1]-newWidthL)/2+newWidthL)]
    croppedRight = frameRight[0:newHeightR, int((sizesR[1]-newWidthR)/2):int((sizesR[1]-newWidthR)/2+newWidthR)]

    frame = np.zeros((newHeightL, newWidthL*2, 3), np.uint8)

    frame[0:newHeightL, 0:newWidthL] = croppedLeft
    frame[0:newHeightR, newWidthL:newWidthR+newWidthL] = croppedRight

    return frame
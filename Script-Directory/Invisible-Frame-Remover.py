from PIL import Image
import glob
import os

path = "C:/Sprites/attacks/"

_, all_attack_directories, _ = zip(*os.walk(path))

def isEmptyFrame(image1):

    im = Image.open(image1, "r")

    pix_val = list(im.getdata()) # Gets the rgba values of an image.

    pix_lists = [list(x) for x in pix_val] # Changes the tuples in pix_val to lists, so we have a list of lists.

    for i in pix_lists: # For every pixel in the list, if the alpha value is ever not 0, it is not an empty frame, return false.

        if i[3] != 0:

            return False

    return True # If we have looked at every pixel, and there have been no pixels with a nonzero alpha value, we have an empty frame, return true.


def emptyFrameMover(images):

    for i in images:  # For every image in the directory, if it is an empty frame, we delete the frame.

        if isEmptyFrame(i) == True:

            os.remove(i)

if __name__ == '__main__':

    for i in all_attack_directories:

        for j in i:

            if (j != "output"): # For every file in the attack directories.

                images = glob.glob("C:/Sprites/attacks/" + j + "/output/*.png")
                emptyFrameMover(images)

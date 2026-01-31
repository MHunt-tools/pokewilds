from PIL import Image
import glob
import os

path = "C:/Sprites/attacks/"

_, all_attack_directories, _ = zip(*os.walk(path))


def mainCall(images, textFile): # The main function call.

    frameNumber = 0
    listOfEmptyFrames = []

    for i in images:  # For every image in the directory, add one to the frame number index, check if it's an empty frame, if it is append the frameNumber to the listOfEmptyFrames

        frameNumber += 1

        if isEmptyFrame(i) == True: #If it is an empty frame, we append it to the listOfEmptyFrames

            listOfEmptyFrames.append(frameNumber)

    inputText(textFile, listOfEmptyFrames)

def inputText(textFile, emptyFrames):

    addedLine = False

    if (len(emptyFrames) == 0): # If there are no empty frames just end the script.

        return

    else:

        with open(textFile) as txt: # Reads the already existing metadata file.

            linesList = txt.readlines()

        txt.close()

        if(len(linesList) == 0): # If the metadata file is empty, we add a line.

            firstLine = str(emptyFrames[0]) + ", invisible_frame\n"
            linesList.append(firstLine)
            addedLine = True

        firstLine = linesList[0]
        top, mid, bot = firstLine.partition(',') # We separate the first number from the comma.

        firstItem = int(top)

        firstIndex = 0

        for i in range(len(emptyFrames)): # For every empty frame we will add text to a linesList.

            lineNumber = emptyFrames[i]

            if (firstItem > lineNumber): # If the first line in the metadata file is a higher number than the first empty frame, we will add the empty frame before it.

                linesList[len(linesList) - 1] = linesList[len(linesList) - 1].strip()
                linesList[len(linesList) - 1] = linesList[len(linesList) - 1] + "\n"

            # If the first number isn't one, we create lines until we get to the first number that was already in metadata.

                if (lineNumber in emptyFrames and addedLine == False):

                    linesList.insert(firstIndex, str(lineNumber) + ", invisible_frame\n")

            elif(lineNumber > len(linesList)): # If the lineNumber is greater than or equal to the number of items in linesList, create a line and add it.

                lastLine = linesList[len(linesList)-1]
                head, sep, tail = lastLine.partition(',')
                index = int(head) + 1

                while(lineNumber >= index): # If the lineNumber is greater than or equal to the current index, if the index is an emptyFrame we append the index with the invisible frame label to the linesList.

                    if (index in emptyFrames):

                        linesList.append(str(index) + "," + " invisible_frame\n")

                    index += 1

            else:

                if(addedLine == False): # If a line wasn't already added before, we add a line. (The only time a line is added before is when a metadata file is empty.)

                    linesList[lineNumber - 1] = linesList[lineNumber - 1].strip()
                    linesList[lineNumber - 1] = linesList[lineNumber - 1] + " invisible_frame\n"  # Adds the invisible frame text.

            firstIndex += 1

            addedLine = False

        linesList[len(linesList) - 1] = linesList[len(linesList) - 1].strip()

        with open(textFile, 'w') as newTxt: # Writes the metadata file with the new linesList.

            newTxt.writelines(linesList) # Writes all the lines from the linesList we created.

def isEmptyFrame(image1):

    im = Image.open(image1, "r")

    pix_val = list(im.getdata()) # Gets the rgba values of an image.

    pix_lists = [list(x) for x in pix_val] # Changes the tuples in pix_val to lists, so we have a list of lists.

    for i in pix_lists: # For every pixel in the list, if the alpha value is ever not 0, it is not an empty frame, return false.

        if i[3] != 0:

            return False

    return True # If we have looked at every pixel, and there have been no pixels with a nonzero alpha value, we have an empty frame, return true.

if __name__ == '__main__':

    for i in all_attack_directories:

        for j in i:

            if (j != "output"): # For every item in the attack directory, call the mainCall function with the images and textFile variables.

                images = glob.glob("C:/Sprites/attacks/" + j + "/output/*.png")
                textFile = "C:/Sprites/attacks/" + j + "/metadata.out"
                mainCall(images, textFile)

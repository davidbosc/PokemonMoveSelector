import win32gui
import win32api
import win32con
import time
import math
from LevenshteinDistance import LevenshteinDistanceService

class Input():

    def __init__(self, text, boundingBoxPoints, heightOffset):
        self.moveText = text
        self.textInterpretations = []

        self.boundingBoxPoints = boundingBoxPoints
        self.minXPosition = min(self.boundingBoxPoints[1][0], self.boundingBoxPoints[0][0])
        self.maxXPosition = max(self.boundingBoxPoints[2][0], self.boundingBoxPoints[3][0])
        self.minYPosition = min(self.boundingBoxPoints[1][1], self.boundingBoxPoints[2][1])
        self.maxYPosition = max(self.boundingBoxPoints[0][1], self.boundingBoxPoints[3][1])
        
        self.heightOffset = heightOffset

    def getInputScreenLocation(self):
        centerXPosition = (self.maxXPosition - self.minXPosition) / 2 + self.minXPosition
        centerYPosition = (self.maxYPosition - self.minYPosition) / 2 + self.minYPosition

        return (centerXPosition, centerYPosition)
            
    def clickInput(self, handle):
        (x, y) = self.getInputScreenLocation()
        # this can be refined, the offset causes issues with my math since the position
        # to send the click is relative to the handle window
        l_param = win32api.MAKELONG(math.floor(x), math.floor(self.heightOffset + (y * 3/4)))
        win32gui.SendMessage(handle, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, l_param)
        time.sleep(0.1)
        win32gui.SendMessage(handle, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, l_param)

    def checkForTextProximityWithinThresholds(self, listOfInputs, heightThreshold, widthThreshold):
        listOfInputsAtSameHeight = list(filter(lambda x: (abs(self.maxYPosition - x.maxYPosition) <= \
            heightThreshold or abs(self.minYPosition - x.minYPosition) <= heightThreshold) and \
                self.minXPosition < x.minXPosition, listOfInputs))
        for input in listOfInputsAtSameHeight:
            areBoundingBoxesWithinThreshold = abs(self.maxXPosition - input.minXPosition) <= widthThreshold
            if areBoundingBoxesWithinThreshold and self.moveText != input.moveText:
                self.moveText += " " + input.moveText
                self.maxXPosition = input.maxXPosition
                listOfInputs.remove(input)

    def autoCorrectText(self, maxWordLength, numberOfWords, words):
        self.textInterpretations = LevenshteinDistanceService(numberOfWords) \
            .LevenshteinDistanceOverMultipleWords(self.moveText, words)
        return self.textInterpretations

    def __str__(self):
        return "<Text: %s, Bounding Box: %s>\n Interpretations: %s, %s, %s\n" % (self.moveText, \
            self.getInputScreenLocation(), self.textInterpretations[0], self.textInterpretations[1], \
                self.textInterpretations[2])
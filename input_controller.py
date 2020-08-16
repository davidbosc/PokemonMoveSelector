import win32gui
import win32api
import win32con
import time
import math

class Input():

    def __init__(self, text, boundingBoxPoints, heightOffset):
        self.moveText = text
        self.boundingBoxPoints = boundingBoxPoints
        self.heightOffset = heightOffset

    def getInputScreenLocation(self):
        minXPosition = min(self.boundingBoxPoints[1][0], self.boundingBoxPoints[0][0])
        maxXPosition = max(self.boundingBoxPoints[2][0], self.boundingBoxPoints[3][0])
        
        minYPosition = min(self.boundingBoxPoints[1][1], self.boundingBoxPoints[2][1])
        maxYPosition = max(self.boundingBoxPoints[0][1], self.boundingBoxPoints[3][1])

        centerXPosition = (maxXPosition - minXPosition) / 2 + minXPosition
        centerYPosition = (maxYPosition - minYPosition) / 2 + minYPosition

        return (centerXPosition, centerYPosition)
            
    def clickInput(self, handle):
        (x, y) = self.getInputScreenLocation()
        # this can be refined, the offset causes issues with my math since the position
        # to send the click is relative to the handle window
        l_param = win32api.MAKELONG(math.floor(x), math.floor(self.heightOffset + (y * 3/4)))
        win32gui.SendMessage(handle, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, l_param)
        time.sleep(0.1)
        win32gui.SendMessage(handle, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, l_param)

    def __str__(self):
        return "<Text: %s, Bounding Box: %s>\n" % (self.moveText, self.getInputScreenLocation())
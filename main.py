import cv2
import numpy as np
from PIL import ImageGrab
import win32gui
import math
from input_controller import Input
import window_handle_util
from text_detection_and_recognition import TextDetectionAndRecognition

emulator_handle = window_handle_util.getWindowHandleFromTitle("DeSmuME")
textInterpreter = TextDetectionAndRecognition()

while True:
    position = win32gui.GetWindowRect(emulator_handle)
    imgHeight = position[3] - position[1]
    positionHeightOffset = position[1]
    position = (position[0], positionHeightOffset + imgHeight / 2, position[2], position[3])
    screenshot = ImageGrab.grab(position)
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

    indices = textInterpreter.detectionOutput(screenshot)

    inputs = []

    for i in indices:
        boundingBoxPoints = []
        wordRecognized = textInterpreter.getDetectedText(screenshot, i, boundingBoxPoints)
        textInterpreter.drawBoundingBoxesAndText(screenshot, wordRecognized)

        # tempMove = Inputs.MoveInput(wordRecognized, boundingBoxPoints)
        # inputs[tempMove.moveText] = tempMove.boundingBoxPoints
        inputs.append(Input(wordRecognized, boundingBoxPoints, position[1] - positionHeightOffset))

    print(*inputs)
    
    for x in inputs:
        if x.moveText == "earth":
            x.clickInput(emulator_handle)

    cv2.imshow('frame', screenshot)
    cv2.waitKey(5)
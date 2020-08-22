import cv2
import numpy as np
from PIL import ImageGrab
import win32gui
import math
from InputController import Input
import WindowHandleUtil
from TextDetectionAndRecognition import TextDetectionAndRecognition
from LevenshteinDistance import LevenshteinDistanceService

movesFile = "pokemon_gen5_moves.txt"

emulatorHandle = WindowHandleUtil.getWindowHandleFromTitle("DeSmuME")
textInterpreter = TextDetectionAndRecognition()
pokemonMoves = [line.rstrip('\n').lower() for line in open(movesFile)]

maxLength = 0
for word in pokemonMoves:
    if len(word) > maxLength:
        maxLength = len(word)

while True:
    position = win32gui.GetWindowRect(emulatorHandle)
    imgHeight = position[3] - position[1]
    imgWidth = position[2] - position[0]
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

        inputs.append(Input(wordRecognized, boundingBoxPoints, position[1] - positionHeightOffset))
    
    scaledYThreshold = imgHeight * 0.02
    scaledXThreshold = imgWidth * 0.1

    for x in list(inputs):
        x.checkForTextProximityWithinThresholds(inputs, scaledYThreshold, scaledXThreshold)

    for x in list(inputs):
        distanceFromCancel = LevenshteinDistanceService().LevenshteinDistanceMatrix(x.moveText, "cancel")[len(x.moveText)-1][5]
        containsPP = " pp" in x.moveText or "pp " in x.moveText or ("pp" in x.moveText and len(x.moveText) == 2)
        if distanceFromCancel < 3 or sum(c.isdigit() for c in x.moveText) > 1 or containsPP:
                inputs.remove(x)
        x.autoCorrectText(maxLength, len(pokemonMoves), pokemonMoves)

    print(*inputs)

    cv2.imshow('frame', screenshot)
    cv2.waitKey(1)
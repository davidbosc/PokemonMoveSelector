import cv2
import numpy as np
from PIL import ImageGrab
import win32gui
import math
from input_controller import Input

detector = cv2.dnn.readNet("frozen_east_text_detection.pb")
recognizer = cv2.dnn.readNet("crnn.onnx")

open_windows = []
out = []

def enum_win(windows_handle_id, result):
    win_text = win32gui.GetWindowText(windows_handle_id)
    open_windows.append((windows_handle_id, win_text))
win32gui.EnumWindows(enum_win, out)

def decodeText(scores):
    text = ""
    alphabet = "0123456789abcdefghijklmnopqrstuvwxyz"
    for i in range(scores.shape[0]):
        c = np.argmax(scores[i][0])
        if c != 0:
            text += alphabet[c - 1]
        else:
            text += '-'

    # adjacent same letters as well as background text must be removed to get the final output
    char_list = []
    for i in range(len(text)):
        if text[i] != '-' and (not (i > 0 and text[i] == text[i - 1])):
            char_list.append(text[i])
    return ''.join(char_list)

def decode(scores, geometry, scoreThresh):
    detections = []
    confidences = []

    ############ CHECK DIMENSIONS AND SHAPES OF geometry AND scores ############
    assert len(scores.shape) == 4, "Incorrect dimensions of scores"
    assert len(geometry.shape) == 4, "Incorrect dimensions of geometry"
    assert scores.shape[0] == 1, "Invalid dimensions of scores"
    assert geometry.shape[0] == 1, "Invalid dimensions of geometry"
    assert scores.shape[1] == 1, "Invalid dimensions of scores"
    assert geometry.shape[1] == 5, "Invalid dimensions of geometry"
    assert scores.shape[2] == geometry.shape[2], "Invalid dimensions of scores and geometry"
    assert scores.shape[3] == geometry.shape[3], "Invalid dimensions of scores and geometry"
    height = scores.shape[2]
    width = scores.shape[3]
    for y in range(0, height):

        # Extract data from scores
        scoresData = scores[0][0][y]
        x0_data = geometry[0][0][y]
        x1_data = geometry[0][1][y]
        x2_data = geometry[0][2][y]
        x3_data = geometry[0][3][y]
        anglesData = geometry[0][4][y]
        for x in range(0, width):
            score = scoresData[x]

            # If score is lower than threshold score, move to next x
            if (score < scoreThresh):
                continue

            # Calculate offset
            offsetX = x * 4.0
            offsetY = y * 4.0
            angle = anglesData[x]

            # Calculate cos and sin of angle
            cosA = math.cos(angle)
            sinA = math.sin(angle)
            h = x0_data[x] + x2_data[x]
            w = x1_data[x] + x3_data[x]

            # Calculate offset
            offset = ([offsetX + cosA * x1_data[x] + sinA * x2_data[x], offsetY - sinA * x1_data[x] + cosA * x2_data[x]])

            # Find points for rectangle
            p1 = (-sinA * h + offset[0], -cosA * h + offset[1])
            p3 = (-cosA * w + offset[0], sinA * w + offset[1])
            center = (0.5 * (p1[0] + p3[0]), 0.5 * (p1[1] + p3[1]))
            detections.append((center, (w, h), -1 * angle * 180.0 / math.pi))
            confidences.append(float(score))

    # Return detections and confidences
    return [detections, confidences]

def fourPointsTransform(frame, vertices):
    vertices = np.asarray(vertices)
    outputSize = (100, 32)
    targetVertices = np.array([
        [0, outputSize[1] - 1],
        [0, 0],
        [outputSize[0] - 1, 0],
        [outputSize[0] - 1, outputSize[1] - 1]], dtype="float32")

    rotationMatrix = cv2.getPerspectiveTransform(vertices, targetVertices)
    result = cv2.warpPerspective(frame, rotationMatrix, outputSize)
    return result

desmume_handle = 0
for(windows_handle_id, win_text) in open_windows:
    if "DeSmuME" in win_text:
        desmume_handle = windows_handle_id

# detector setup
inWidth = 320
inHeight = 320
output_layer = []
output_layer.append("feature_fusion/Conv_7/Sigmoid")
output_layer.append("feature_fusion/concat_3")

# recognizer setup
tickmeter = cv2.TickMeter()

while True:

    position = win32gui.GetWindowRect(desmume_handle)
    imgWidth = position[2] - position[0]
    imgHeight = position[3] - position[1]
    #get lower half of DS screen
    newPos = (position[0], position[1] + (imgHeight / 2), position[2], position[3])
    # newPos = (position[0], position[1], position[2], position[3])
    screenshot = ImageGrab.grab(newPos)
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

    image_blob = cv2.dnn.blobFromImage(screenshot, 1.0, (inWidth, inHeight), (123.68, 116.78, 103.94),  swapRB=True, crop=False)

    detector.setInput(image_blob)
    output = detector.forward(output_layer)
    scores = output[0]
    geometry = output[1]

    confThreshold = 0.5
    nmsThreshold = 0.3
    [boxes, confidences] = decode(scores, geometry, confThreshold)
    indices = cv2.dnn.NMSBoxesRotated(boxes, confidences, confThreshold, nmsThreshold)

    height_ = screenshot.shape[0]
    width_ = screenshot.shape[1]
    rW = width_ / float(inWidth)
    rH = height_ / float(inHeight)

    inputs = []

    for i in indices:
        # get 4 corners of the rotated rect
        boundingBoxPoints = []
        vertices = cv2.boxPoints(boxes[i[0]])
        for x in vertices[0:4]:
            boundingBoxPoints.append(x[0:2])
        # scale the bounding box coordinates based on the respective ratios
        for j in range(4):
            vertices[j][0] *= rW
            vertices[j][1] *= rH

        # get cropped image using perspective transform
        cropped = fourPointsTransform(screenshot, vertices)
        cropped = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)

        # Create a 4D blob from cropped image
        blob = cv2.dnn.blobFromImage(cropped, size=(100, 32), mean=127.5, scalefactor=1 / 127.5)
        recognizer.setInput(blob)
        
        # Run the recognition model
        tickmeter.start()
        result = recognizer.forward()
        tickmeter.stop()

        # decode the result into text
        wordRecognized = decodeText(result)
        cv2.putText(screenshot, wordRecognized, (int(vertices[1][0]), int(vertices[1][1])), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (255, 0, 0))

        for j in range(4):
            p1 = (vertices[j][0], vertices[j][1])
            p2 = (vertices[(j + 1) % 4][0], vertices[(j + 1) % 4][1])
            cv2.line(screenshot, p1, p2, (0, 255, 0), 1)

        # tempMove = Inputs.MoveInput(wordRecognized, boundingBoxPoints)
        # inputs[tempMove.moveText] = tempMove.boundingBoxPoints
        inputs.append(Input(wordRecognized, boundingBoxPoints, newPos[1] - position[1]))

    print(*inputs)
    
    for x in inputs:
        if x.moveText == "fight":
            x.clickInput(desmume_handle)

    cv2.imshow('frame', screenshot)
    cv2.waitKey(15)
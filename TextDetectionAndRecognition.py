import cv2
import math
import numpy as np

class TextDetectionAndRecognition():

    def __init__(self):
        self.detector = cv2.dnn.readNet("./frozen_east_text_detection.pb")
        self.recognizer = cv2.dnn.readNet("./crnn.onnx")
        # detector setup
        self.inWidth = 320
        self.inHeight = 320
        self.output_layer = []
        self.output_layer.append("feature_fusion/Conv_7/Sigmoid")
        self.output_layer.append("feature_fusion/concat_3")
        # recognizer setup
        self.tickmeter = cv2.TickMeter()

    def __decodeText(self,scores):
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

    def __decode(self, scores, geometry, scoreThresh):
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

    def __fourPointsTransform(self, frame, vertices):
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

    def detectionOutput(self, screenshot):
        image_blob = cv2.dnn.blobFromImage(screenshot, 1.0, (self.inWidth, self.inHeight), \
            (123.68, 116.78, 103.94),  swapRB=True, crop=False)

        self.detector.setInput(image_blob)
        output = self.detector.forward(self.output_layer)
        scores = output[0]
        geometry = output[1]

        confThreshold = 0.5
        nmsThreshold = 0.3
        [self.boxes, self.confidences] = self.__decode(scores, geometry, confThreshold)
        indices = cv2.dnn.NMSBoxesRotated(self.boxes, self.confidences, confThreshold, nmsThreshold)

        height_ = screenshot.shape[0]
        width_ = screenshot.shape[1]
        self.rW = width_ / float(self.inWidth)
        self.rH = height_ / float(self.inHeight)

        return indices

    def getDetectedText(self, screenshot, textIndex, boundingBoxPointsOut):
        self.vertices = cv2.boxPoints(self.boxes[textIndex[0]])
        for x in self.vertices[0:4]:
            boundingBoxPointsOut.append(x[0:2])
        
        for j in range(4):
            self.vertices[j][0] *= self.rW
            self.vertices[j][1] *= self.rH

        # get cropped image using perspective transform
        cropped = self.__fourPointsTransform(screenshot, self.vertices)
        cropped = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)

        # Create a 4D blob from cropped image
        blob = cv2.dnn.blobFromImage(cropped, size=(100, 32), mean=127.5, scalefactor=1 / 127.5)
        self.recognizer.setInput(blob)
        
        # Run the recognition model
        self.tickmeter.start()
        result = self.recognizer.forward()
        self.tickmeter.stop()

        # decode the result into text
        return self.__decodeText(result)

    def drawBoundingBoxesAndText(self, screenshot, text):
        cv2.putText(screenshot, text, (int(self.vertices[1][0]), int(self.vertices[1][1])), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0))

        for j in range(4):
            p1 = (self.vertices[j][0], self.vertices[j][1])
            p2 = (self.vertices[(j + 1) % 4][0], self.vertices[(j + 1) % 4][1])
            cv2.line(screenshot, p1, p2, (0, 255, 0), 1)
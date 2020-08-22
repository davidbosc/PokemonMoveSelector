import numpy as np
from time import time

class LevenshteinDistanceService:

    def __init__(self, numberOfWords = 1):
        self.numberOfWords = numberOfWords

    def LevenshteinDistanceMatrix(self, a, b):
        distance = np.zeros((len(a),len(b)), dtype = int)

        for i in range(1, len(a)):
                distance[i][0] = i

        for i in range(1, len(b)):
                distance[0][i] = i

        for j in range(1,  len(b)):
            for i in range(1,len(a)):
                if a[i] == b[j]:
                    substitutionCost = 0
                else:
                    substitutionCost = 1
                distance[i][j] = min(distance[i-1, j] + 1, distance[i, j-1] + 1, \
                    distance[i-1, j-1] + substitutionCost)

        return distance

    def LevenshteinDistanceOverMultipleWords(self, inputWord, possibleWords):
        output = []
        
        for i in range(self.numberOfWords):
            distance = self.LevenshteinDistanceMatrix(inputWord, possibleWords[i])
            output.append((possibleWords[i], distance[len(inputWord)-1][len(possibleWords[i])-1]))
        
        return sorted(output, key=lambda x: x[1])
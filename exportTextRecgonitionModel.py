#see the below repo for the original code to export this model  
# https://github.com/opencv/opencv/blob/master/samples/dnn/text_detection.py

#download the model here:
# https://github.com/meijieru/crnn.pytorch

import torch
import extern.crnn_pytorch.models.crnn as CRNN

model = CRNN.CRNN(32, 1, 37, 256)
model.load_state_dict(torch.load('.\extern\crnn_pytorch\data\crnn.pth'))
dummy_input = torch.randn(1, 1, 32, 100)
torch.onnx.export(model, dummy_input, "crnn.onnx", verbose=True)
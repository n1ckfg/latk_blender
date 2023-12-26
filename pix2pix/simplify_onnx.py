# https://github.com/daquexian/onnx-simplifier

import onnx
from onnxsim import simplify
import sys

argv = sys.argv
argv = argv[argv.index("--") + 1:]  # get all args after "--"
inputUrl = str(argv[0])

model = onnx.load(inputUrl)

model_simp, check = simplify(model)
assert check, "Simplified ONNX model could not be validated"

outputUrl = inputUrl.split(".onnx")[0] + "_simplified.onnx"
onnx.save(model_simp, outputUrl)

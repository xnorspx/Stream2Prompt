from ultralytics import YOLO

model = YOLO("model-lab/yolo11/yolo11s.pt")

# Train the model
train_results = model.train(
    data="model-lab/dataset/data.yaml",  # path to dataset YAML
    epochs=100,  # number of training epochs
    imgsz=640,  # training image size
    device=0,  # device to run on, i.e. device=0 or device=0,1,2,3 or device=cpu
)

# Evaluate model performance on the validation set
metrics = model.val()

# Perform object detection on an image
results = model("/home/xnorspx/Projects/Stream2Prompt/model-lab/dataset/images/test/20250823_180435(0).jpg")
results[0].show()

# Export the model to ONNX format
path = model.export(format="engine", half=True, dynamic=True, device=0)  # return path to exported model

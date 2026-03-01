from ultralytics import YOLO
import torch

device = "xpu" if torch.xpu.is_available() else "cpu"

model = YOLO("yolo26n.pt")  # or yolov8n.pt

# Train with 180-degree rotation and 50% vertical flip probability
model.train(
    data="kitti.yaml", 
    epochs=3, 
    degrees=180.0, 
    flipud=0.5
)
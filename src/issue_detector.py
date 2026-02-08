import pathlib
from huggingface_hub import hf_hub_download
import torch

repo_id = "Javiai/3dprintfails-yolo5vs"
filename = "model_torch.pt"
model_folder = pathlib.Path(__file__).parent.resolve().joinpath("model")

model_path = hf_hub_download(repo_id=repo_id, filename=filename, local_dir=model_folder)


model = torch.hub.load('Ultralytics/yolov5', 'custom', model_path, verbose=False)

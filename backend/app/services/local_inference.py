import sys
import numpy as np
import torch
import torch.nn as nn
import torchvision.transforms as transforms
import boto3
from PIL import Image
from facenet_pytorch import MTCNN, InceptionResnetV1, fixed_image_standardization
from openai import OpenAI
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from services import config 
from pathlib import Path
import time 
from services import LLM_utils, s3_utils


# Note: this file is used to do inference at EC2 server directly. This is due to the current resource limitation. We could not afford to create SageMaker endpoint at prototype stage
# and use SageMaker training job takes even more time to prepare for container image.

device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
parent_dir = Path(__file__).resolve().parent.parent
new_folder = parent_dir / "temp"

# Create the folder (and any necessary parent folders) if it doesn't exist
new_folder.mkdir(parents=True, exist_ok=True)
temp_dir = str(new_folder.resolve())
if os.path.exists(temp_dir):
    os.makedirs(temp_dir, exist_ok=True)

s3_client = boto3.client('s3', aws_access_key_id= config.S3_ACCESS_KEY_ID,
    aws_secret_access_key= config.S3_SECRET_ACCESS_KEY,
    region_name=config.AWS_REGION)

class FinetunedInceptionResnetV1(nn.Module):
    def __init__(self, model, num_classes):
        super(FinetunedInceptionResnetV1, self).__init__()
        self.backbone = model
        self.backbone.logits = nn.Linear(self.backbone.last_linear.out_features, num_classes)

        # Freeze all layers except the last fully connected layer
        for param in self.backbone.parameters():
            param.requires_grad = False
        for param in self.backbone.last_linear.parameters():
            param.requires_grad = True
        for param in self.backbone.last_bn.parameters():
            param.requires_grad = True
        for param in self.backbone.logits.parameters():
            param.requires_grad = True

    def forward(self, x):
        x = self.backbone(x)
        return x

Base = declarative_base()
class UserRemindee(Base):
    __tablename__ = 'user_remindee'

    remindee_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False)
    image_object_key = Column(String, nullable=False)
    person_name = Column(String, nullable=False)
    summary = Column(String, nullable=True)
    relationship = Column(String, nullable=False)
        
def face_detection(device, image, image_key):
    # Define MTCNN model for facial detection
    mtcnn = MTCNN(
        image_size=160, margin=0, min_face_size=20,
        thresholds=[0.6, 0.7, 0.7], factor=0.709, post_process=True,
        device=device
    )
    transform = transforms.Resize((512, 512))
    img_resized = transform(image)
    mtcnn(img_resized)
    del mtcnn
    return img_resized

def load_model(user_id, device):
    s3_path = user_id + '/model.pth'
    

    os.makedirs(temp_dir + f"/{user_id}", exist_ok= True)
    if os.path.exists(temp_dir + f"/{user_id}/model.pth"):
        os.remove(temp_dir + f"/{user_id}/model.pth")

    local_model_path = temp_dir + f'/{user_id}/model.pth'  # Local path to download the model
    
    try:
        s3_client.download_file(config.S3_MODEL_WEIGHT_BUCKET_NAME, s3_path, local_model_path)
        print(f"Model downloaded from S3 to {local_model_path}")
    except Exception as e:
        print(f"Error downloading model from S3: {e}")
        return None, None, None
    
    checkpoint = torch.load(local_model_path, map_location=device)
    num_classes = checkpoint['num_classes']
    class_names = checkpoint['class_names']

    model = FinetunedInceptionResnetV1(InceptionResnetV1(classify=True, pretrained='vggface2'), num_classes=num_classes)
    model.load_state_dict(checkpoint['state_dict'])
    model.to(device)
    model.eval()
    return model, num_classes, class_names

def get_summary(user_id, remindee_name):
    relationship, accumulated_summary = LLM_utils.get_accumulated_descriptions_for_remindee(user_id, remindee_name)
    ai_summary, image_obj_key  = LLM_utils.generate_summary_for_remindee(user_id, remindee_name, relationship, accumulated_summary)
    # sometimes the LLM will generate strange resul
    image_obj_key = f"{user_id}/{remindee_name}/{image_obj_key}"
    presigned_url = s3_utils.get_image_url_from_s3(image_obj_key)['presigned_url']
    
    remindee_info = {"name": remindee_name,
                     "relationship": relationship.strip(),
                     "accumulated_summary": accumulated_summary.strip(),
                     "ai_summary": ai_summary,
                     "image_url": presigned_url}
    return remindee_info
    
    
def local_inference(user_id, image_s3_url):
    timestamp = int(time.time())  
    unique_file_name = f"{timestamp}_image.jpg"
    
    if not os.path.exists(f"{temp_dir}/{user_id}"):
        os.makedirs(f"{temp_dir}/{user_id}", exist_ok=True)

    local_path = f"{temp_dir}/{user_id}/{unique_file_name}"
    s3_client.download_file(config.S3_MODEL_WEIGHT_BUCKET_NAME, image_s3_url, local_path)
    image = Image.open(local_path).convert("RGB")

    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    image = face_detection(device, image, image)
    model, num_classes, class_names = load_model(user_id, device)
    
    # if the user is the first time to do identify, but has not trained yet, exit directly
    if model is None: 
        return None

    # inference
    trans = transforms.Compose([
        np.float32,
        transforms.ToTensor(),
        fixed_image_standardization
    ])
    
    image = Image.open(local_path).convert("RGB")
    # Apply transformations to the image
    image_tensor = trans(image)
    image_tensor = image_tensor.unsqueeze(0).to(device)
    
    with torch.no_grad():
        output = model(image_tensor)
        probs = torch.softmax(output, dim=1)  # Convert logits to probabilities
        print(probs)
        confidence, predicted_class = torch.max(probs, 1) # Get predicted class
        print("predicted_class:", predicted_class, "class_name:", class_names)
        print("confidence:", confidence)
        
        # remove the temporary image file
        if os.path.exists(local_path):
            os.remove(local_path)
            
        if confidence >= .5:
            print(f"Predicted Class: {predicted_class.item()}")
            person = class_names[predicted_class.item()]
            print(f"Predicted Person: {person}")
        else:
            print("could not identify the person.")
            return "NA"
            
    # get summary of predicted person
    summary = get_summary(user_id, person)
    return summary
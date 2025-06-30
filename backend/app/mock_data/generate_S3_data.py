
import boto3
import os
from app.services import config 
import random

# import ssl
# import certifi
# ssl_context = ssl.create_default_context(cafile=certifi.where())

'''

d96a955c-b061-7080-194e-7e597383cad9: enquiry@thecodingfun.com

d9aa357c-20d1-704c-3877-63edc40201bd: claudia.yao2012@gmail.com

c9da252c-9041-7089-170c-be754918cc8d: e1331095@u.nus.edu

'''

random_user_ids = ['d96a955c-b061-7080-194e-7e597383cad9', 
                   'd9aa357c-20d1-704c-3877-63edc40201bd',
                   'c9da252c-9041-7089-170c-be754918cc8d']
person_names=["Shala", "Tera", "Draren", "Catheline", "David Chan", "Sandra Wong", "Sandra Lee", "Kris Tan", "Mark Song",
              "Sean", "Steve", "Dave", "Reel", "Sandra Cathe", "Apple Lee", "Weifeng Sun", "Bob Luo", "Mike Lee"]


# Initialize the S3 client
s3_client = boto3.client("s3", 
                         aws_access_key_id= config.S3_ACCESS_KEY_ID,
                         aws_secret_access_key= config.S3_SECRET_ACCESS_KEY,
                         region_name=config.AWS_REGION)

# Define your S3 bucket name
bucket_name = config.S3_IMAGE_STORAGE_BUCKET_NAME

# Directory where your images are located
image_dir = '/Users/evansun/Documents/remindme_test_images'

persons = os.listdir(image_dir)

for person in persons:
    user_id = random.choice(random_user_ids)
    person_folder = os.path.join(image_dir, person)
    person_name = random.choice(person_names) + "_" + "".join([chr(random.randint(97, 122)) for _ in range(5)])

    
    if os.path.isdir(person_folder):
        num = 0
        for file_name in os.listdir(person_folder):
            local_file_path = os.path.join(person_folder, file_name)
            
            if os.path.isfile(local_file_path) and file_name.lower().endswith(('jpg', 'jpeg', 'png', 'gif')):
                print(f"{user_id}/{person_name}/{file_name}")
                num += 1
                s3_object_key = f"{user_id}/{person_name}/{file_name}"  # Set object key in S3
                s3_client.upload_file(local_file_path, bucket_name, s3_object_key)

                if num > 10:
                    break
                    

print("All images uploaded successfully.")






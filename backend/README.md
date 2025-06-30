### pip install git+https://github.com/facebookresearch/nougat.git

# Backend Specification

**Visit this video for some important information of backend development:** https://drive.google.com/file/d/17nQt_FnB28rv005JQg8egHnEGrFzwE6O/view?usp=sharing

## Running Backend:

1. Switch current folder to project root folder.
2. Type "python install -r requirements.txt" to intall required packages.
3. Switch current folder to backend
4. Type "python install -r requirements.txt" to intall required packages for backend.
5. **In a new terminal, type "redis-server"**
6. Go to AWS management console, and make the RDS instance `remind-me-instance` running (it is stopped for cost saving in development phase)
7. In a new terminal, type "python app/main.py"

If everything runs correctly, now you could:<br>

- Visit the website at http://localhost:8000<br>
- Visit API documentation at: http://127.0.0.1:8000/docs (_not working now_)

## FastAPI Endpoints:

- Get `/user/login`: the front end informs backend the user login event. This endpoint is used to set Redis expiration state.
- Get `/user/signout`: the front end informs backend the user sign out event. This endpoint is used to update Redis expiration state.
- Get `/user/user-profile`: get current user's information<br>
- Get `/user/profile`: get randomly chosen remindees' information (max. 5 remindees)<br>
- Post `/user/update-profile`: update current user's information, such as nick-name, avatar-image, phone number, etc.<br>
- Post `/operation/upload`: upload one or multiple images related to one remindee<br>
- Post `operation/identify`: trigger inference task
- Post `/operaion/check-inference-status`: check inference task to see if it completed/failed/stopped, etc.
- Post `/operation/get-inference-result`: get inference result from SageMaker job.
- Post `/operation/train`: trigger training task
- Post `/operation/check-train-status`: check training status of the specified SageMaker work

## Run Postman to check endpoint:

1. Import the file into Postman from `backend/test/backend_image_processing.postman_collection.json`
2. After running frontend and login in with any account, choose Inspect from context menu of browser. Switch to Console tab and copy the whole bearer token.
3. Paste the token to the Token field of Authentication tab in Postman.
4. Run each query, and customize the input parameters.

## Amazon S3 buckets

- Image storage: remind-me-image-storage <br>
  Virtual folder structure is: <user_id>/<remindee_name>/<file_name><br>
  This bucket contains both remindee images and user avatar images. <br>
  All the avatar images are located under avatar/<user_id>.jpg<br>

- Model storage: remind-me-deep-learning-models

## Amazon Postgresql

- Use PgAdmin or other database management tool to view/edit the data. <br>

  - Host name/address: remind-me-instance.czsmms6yqdmh.ap-southeast-1.rds.amazonaws.com

- You could find this database instance at AWS: `RDS/databases/remind-me-instance`

- Table user_remindee:

  - `remindee_id`: just a sequential id
  - `user_id`: this column is the foreign key of table user_summary's user_id
  - `image_object_key`: store the object key of the S3 bucket `remind-me-image-storage`
  - `person_name`: string type, not null
  - `summary`: summary, or tag for this remindee image. string type, nullable
  - `relationship`: string type, not null
  - `created_at`: automatic setting
  - `updated_at`: automatic setting

- Table user_summary:
  - `user_id`: comes from Cognito user_id
  - `nick_name`: string type, nullable
  - `description`: string, nullable
  - `age`: integer, nullable
  - `phone_number`: string type, nullable
  - `created_at`: automatic setting
  - `updated_at`: automatic setting
  - `avatar_object_key`: store the avatar objecct key of the user at the S3 bucket. not nullable.

Table remindee_summary:

- `user_id`: string type, comes from Cognito user_id
- `person_name`: string type, remindee person_name, same value as table user_remindee's person_name
- `summary`: string type, LLM AI generated summary

# Redis database

- It will be hosted together with the application together on EC2. No extra setting is needed.

## About Project Settings

- All the access key id, security key, user id, password, etc. is stored in .env

## Backend File Structure

- Folder `mock_data`: the scripts in this folder are used to fill in the initial data of PostgreSQL tables and AWS S3 image bucket.
- Folder `routers`: The folder contains the API endpoints.
- Folder `services`: The folder contain the logic and database related operation, configuration, etc.
- Folder `test`: The folder contains postman query file which could be imported to test endpoints.

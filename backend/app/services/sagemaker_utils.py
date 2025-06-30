import boto3
from botocore.exceptions import ClientError
import time
from fastapi import HTTPException
import botocore.exceptions
from services import config

# refer to this list for sagemaker instance and price https://aws.amazon.com/sagemaker-ai/pricing/
# check this for the sagemaker quota https://ap-southeast-1.console.aws.amazon.com/servicequotas/home/services/sagemaker/quotas

# Initialize Boto3 client
sagemaker_client = boto3.client(
    "sagemaker",
    aws_access_key_id=config.S3_ACCESS_KEY_ID,
    aws_secret_access_key=config.S3_SECRET_ACCESS_KEY,
    region_name=config.AWS_REGION,
)

s3_client = boto3.client("s3",
                        aws_access_key_id=config.S3_ACCESS_KEY_ID,
                        aws_secret_access_key=config.S3_SECRET_ACCESS_KEY,
                        region_name=config.AWS_REGION)
        

# this function is used when we want to change the key of S3 object
async def adjust_model_key(old_key, new_key):
    try:
        if object_exists(config.S3_MODEL_WEIGHT_BUCKET_NAME, old_key):
            s3_client.copy_object(Bucket=config.S3_MODEL_WEIGHT_BUCKET_NAME,
                        CopySource={'Bucket': config.S3_MODEL_WEIGHT_BUCKET_NAME, 'Key': old_key},
                        Key=new_key)

            # Delete the old object
            s3_client.delete_object(Bucket=config.S3_MODEL_WEIGHT_BUCKET_NAME, Key=old_key)

        return True
    except ClientError as e:
        raise HTTPException(400, f"{e}") 
    
# this function is used to check if an S3 key exists
def object_exists(bucket, key):
    try:
        s3_client.head_object(Bucket=bucket, Key=key)
        return True
    except ClientError as e:
        return False
        
# Note: this function is to use processing job of sagemaker to do inference. (It could not run since it needs service quota)
def trigger_sagemaker_inference_job(user_id: str, image_bytes: bytes):
    timestamp = str(int(time.time()))
    inference_job_name = f"infer-{user_id}-{timestamp}"

    object_key = f"{user_id}/{inference_job_name}/image.jpg"
    try:
        s3_client.put_object(Bucket=config.S3_MODEL_WEIGHT_BUCKET_NAME, Key=object_key, Body=image_bytes, ContentType="image/jpeg")
    except Exception as e:
        raise HTTPException("error uploading to S3:", f"{e}")

    container_image_uri = '763104351884.dkr.ecr.ap-southeast-1.amazonaws.com/pytorch-inference:1.13.1-cpu-py39-ubuntu20.04' 
    model_s3_uri = f"s3://{config.S3_MODEL_WEIGHT_BUCKET_NAME}/{user_id}/model.pth"
    inference_script_uri = f's3://{config.S3_MODEL_WEIGHT_BUCKET_NAME}/{user_id}/inference.py'
    output_s3_uri = f's3://{config.S3_MODEL_WEIGHT_BUCKET_NAME}/{user_id}/{inference_job_name}/output/'

    # Define the processing job parameters
    processing_inputs = [
        {
            'InputName': 'model',
            'S3Input': {
                'S3Uri': model_s3_uri,
                'LocalPath': '/opt/ml/processing/input/model',
                'S3DataType': 'S3Prefix', 
                'S3InputMode': 'File'
            }
        },
        {
            'InputName': 'inference_script',
            'S3Input': {
                'S3Uri': inference_script_uri,
                'LocalPath': '/opt/ml/processing/input/code',
                'S3DataType': 'S3Prefix',  # Use the prefix to specify the folder in S3
                'S3InputMode': 'File'
            }
        },
    ]

    processing_outputs = [
        {
            'OutputName': 'output',
            'S3Output': {
                'S3Uri': output_s3_uri,
                'LocalPath': '/opt/ml/processing/output',
                'S3UploadMode': 'EndOfJob'
            }
        }
    ]

    processing_job_params = {
        'ProcessingJobName': inference_job_name,
        'RoleArn': config.SAGEMAKER_ROLE_ARN,
        'AppSpecification': {
            'ImageUri': container_image_uri,
            'ContainerEntrypoint': ['python3', '/opt/ml/processing/input/code/inference.py']  # Entry point to your script
        },
        'ProcessingInputs': processing_inputs,
        'ProcessingOutputConfig': {
            'Outputs': processing_outputs
        },
        'ProcessingResources': {
            'ClusterConfig': {
                'InstanceCount': 1,
                'InstanceType': 'ml.m5.large',  
                'VolumeSizeInGB': 30 
            }
        }
    }

    # Create the processing job using the SageMaker client
    try:
        response = sagemaker_client.create_processing_job(**processing_job_params)
        return {"message": "Inference job started", "JobName": inference_job_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting inference job: {e}")


# NOte: we are using sagemaker_client.create_training_job to do inference to walk around service quota issue. Currently, we do not want 
# to apply for batch transform or processing job service quota due to potential cost

def trigger_sagemaker_inference_job_new(user_id: str, object_key):
    try: 
        timestamp = str(int(time.time()))
        inference_job_name = f"infer-{user_id}-{timestamp}"    
        
        input_folder = f"s3://{config.S3_IMAGE_STORAGE_BUCKET_NAME}/{user_id}/"
        output_folder = f"s3://{config.S3_MODEL_WEIGHT_BUCKET_NAME}/{user_id}/"
        
        response = sagemaker_client.create_training_job(
            TrainingJobName=inference_job_name,
            AlgorithmSpecification={
                "TrainingImage": "763104351884.dkr.ecr.ap-southeast-1.amazonaws.com/pytorch-training:2.0.1-cpu-py310",  # Change this to your custom image
                "TrainingInputMode": "File"
            },
            RoleArn=config.SAGEMAKER_ROLE_ARN,
            InputDataConfig=[
                {
                    "ChannelName": "training",
                    "DataSource": {
                        "S3DataSource": {
                            "S3DataType": "S3Prefix",
                            "S3Uri": input_folder,
                            "S3DataDistributionType": "FullyReplicated"
                        }
                    },
                    "ContentType": "application/x-image",
                }
            ],
            OutputDataConfig={
                "S3OutputPath": output_folder
            },
            ResourceConfig={
                "InstanceType": "ml.m5.large",
                "InstanceCount": 1,
                "VolumeSizeInGB": 10,
            },
            StoppingCondition={
                "MaxRuntimeInSeconds": 500
            },
            
            HyperParameters={
                "sagemaker_program": "\"inference.py\"",
                "sagemaker_submit_directory": f"\"s3://{config.S3_MODEL_WEIGHT_BUCKET_NAME}/inference.tar.gz\"",
                "user_id":f"\"{user_id}\"",
                "image_key": f"\"{object_key}\"",
                
            }
        )
        return {"status": response["ResponseMetadata"]["HTTPStatusCode"], "inference-job-name": inference_job_name}
        
    except botocore.exceptions.ClientError as e:
        raise HTTPException(400, e.response["Error"]["Message"])
        
        
        
def trigger_sagemaker_training_job(user_id: str):
    try: 
        timestamp = str(int(time.time()))
        # job_name should be unique, so it could be tracked in multitenancy env.
        job_name = f"train-{user_id}-{timestamp}"
        
        input_folder = f"s3://{config.S3_IMAGE_STORAGE_BUCKET_NAME}/{user_id}/"
        output_folder = f"s3://{config.S3_MODEL_WEIGHT_BUCKET_NAME}/{user_id}/"
        
        response = sagemaker_client.create_training_job(
            TrainingJobName=job_name,
            AlgorithmSpecification={
                "TrainingImage": "763104351884.dkr.ecr.ap-southeast-1.amazonaws.com/pytorch-training:2.0.1-cpu-py310",  # Change this to your custom image
                "TrainingInputMode": "File"
            },
            RoleArn=config.SAGEMAKER_ROLE_ARN,
            InputDataConfig=[
                {
                    "ChannelName": "training",
                    "DataSource": {
                        "S3DataSource": {
                            "S3DataType": "S3Prefix",
                            "S3Uri": input_folder,
                            "S3DataDistributionType": "FullyReplicated"
                        }
                    },
                    "ContentType": "application/x-image",
                }
            ],
            OutputDataConfig={
                "S3OutputPath": output_folder
            },
            ResourceConfig={
                "InstanceType": "ml.m5.large",
                "InstanceCount": 1,
                "VolumeSizeInGB": 10,
            },
            StoppingCondition={
                "MaxRuntimeInSeconds": 500
            },
            
            HyperParameters={
                "sagemaker_program": "\"train.py\"",
                "sagemaker_submit_directory": f"\"s3://{config.S3_MODEL_WEIGHT_BUCKET_NAME}/train.tar.gz\"",
                "user_id":f"\"{user_id}\""
                
            }
        )
        return {"status": response["ResponseMetadata"]["HTTPStatusCode"], "training-job-name": job_name}
        
    except botocore.exceptions.ClientError as e:
        raise HTTPException(400, e.response["Error"]["Message"])
        
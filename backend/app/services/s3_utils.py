import boto3
from services import config
from fastapi import HTTPException
from services import config

s3_image_client = boto3.client("s3", 
                         aws_access_key_id= config.S3_ACCESS_KEY_ID,
                         aws_secret_access_key= config.S3_SECRET_ACCESS_KEY,
                         region_name=config.AWS_REGION)

s3_model_client = boto3.client("s3", 
                         aws_access_key_id= config.S3_ACCESS_KEY_ID,
                         aws_secret_access_key= config.S3_SECRET_ACCESS_KEY,
                         region_name=config.AWS_REGION)

# upload images to S3 bucket: S3_IMAGE_STORAGE_BUCKET_NAME
def upload_image_to_s3(object_key: str, file_content: bytes) -> str:
    try:
        s3_image_client.put_object(Bucket=config.S3_IMAGE_STORAGE_BUCKET_NAME, Key=object_key, Body=file_content, ContentType="image/jpeg")
        return f"s3://{config.S3_IMAGE_STORAGE_BUCKET_NAME}/{object_key}"
    except Exception as e:
        raise HTTPException("error uploading to S3:", f"{e}")


def get_image_url_from_s3(object_key: str, expiration: int = 3600):
    try:
        # Generate a pre-signed URL for the file with a 1-hour expiration time
        expiration = 3600  # 1 hour
        presigned_url = s3_image_client.generate_presigned_url('get_object',
                                                  Params={'Bucket': config.S3_IMAGE_STORAGE_BUCKET_NAME, 'Key': object_key},
                                                  ExpiresIn=expiration)
        return {"presigned_url": presigned_url}
    
    except Exception as e:
        raise HTTPException(400, f"{e}")
    
# get face recognition model url from S3 bucket: S3_IMAGE_STORAGE_BUCKET_NAME
def get_model_url_from_s3(object_key: str, expiration: int = 3600):
    try:
        url = s3_model_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": config.S3_MODEL_WEIGHT_BUCKET_NAME, "Key": object_key},
            ExpiresIn=expiration
        )
        return url
    except Exception as e:
        raise HTTPException(400, f"{e}")
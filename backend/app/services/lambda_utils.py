import boto3
import json
from services import config
from fastapi import HTTPException


lambda_client = boto3.client("lambda", region_name=config.AWS_REGION)

def invoke_lambda(user_id: str, raw_image_data: str):
    
    
    payload = {
            "user_id": user_id,
            "raw_image_data": raw_image_data  # Send the raw image data directly
        }

    try:
        response = lambda_client.invoke(
            FunctionName=config.LAMBDA_FUNCTION_NAME,
            InvocationType="Event",  # Async execution
            Payload=json.dumps(payload)
        )
        return json.loads(response["Payload"].read().decode("utf-8"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling Lambda: {str(e)}")


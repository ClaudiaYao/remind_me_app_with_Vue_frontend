

from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException
from typing import Dict, List
from sqlalchemy.orm import Session
from routers import utils
import time
from services import LLM_utils, queue_manager, redis_utils, database, congnito_auth, s3_utils, config
import uuid
import botocore
from pathlib import Path
import redis.asyncio as redis
from routers import utils


router = APIRouter(
    prefix="/operation",
    tags=["operation"],
    responses={404: {"description": "Not found this API route."}},
)

parent_dir = Path(__file__).resolve().parent.parent
temp_folder = parent_dir / "temp"


@router.post("/cancel/{job_id}")
def cancel_job(job_id: str):
    if not redis_utils.redis_client.exists(job_id):
        raise HTTPException(status_code=404, detail="Job not found")
    
    redis_utils.redis_client.hset(job_id, "status", "cancelled")
    return {"message": f"Job {job_id} cancelled."}


@router.get("/is-model-exist")
async def is_model_exist(user: Dict = Depends(congnito_auth.get_current_user)):
    try:
        s3_utils.s3_client.head_object(Bucket=config.S3_MODEL_WEIGHT_BUCKET_NAME, Key=f"{user['sub']}/model.pth")
        return {"status": True}
    except Exception as e:
        return {"status": False}
    
@router.post("/identify")
async def identify(
    file: UploadFile = File(...),
    user: Dict = Depends(congnito_auth.get_current_user)):
    
    try:
        if not file:
            raise HTTPException(status_code=400, detail="No files uploaded")

        print("get file")
        # for demo
        # if LOCAL_INFERENCE:
        #     object_key = f"{user_id}/image.jpg"
            
        #     try:
        #         s3_utils.s3_model_client.put_object(Bucket=config.S3_MODEL_WEIGHT_BUCKET_NAME, Key=object_key, Body=image_bytes, ContentType="image/jpeg")
        #     except Exception as e:
        #         raise HTTPException("error uploading to S3:", f"{e}")
            
        #     summary = local_inference.local_inference(user_id, object_key)
            
        #     local_file_path = f"{local_inference.temp_dir}/{user_id}/result.json"
        #     if summary is None:
        #         return utils.ApiResponse(success=False,
        #             message="model does not exist",
        #             data=None)
                                
        #     elif isinstance(summary, dict):
        #         with open(local_file_path, "w") as f:
        #             json.dump(summary, f, indent=4)
                
        #         return utils.ApiResponse(success=True,
        #                 message="Completed",
        #                 data={"person": summary['name'],
        #                     "summary": summary["ai_summary"],
        #                     "image": summary["image_url"]})
                
        #     elif isinstance(summary, str) and summary =="NA":
        #         if os.path.exists(local_file_path):
        #             os.remove(local_file_path)
            
        #         return utils.ApiResponse(success=True,
        #                 message="Completed",
        #                 data={"person": "Cannot identify the face",
        #                     "summary": "Your AI assistant feels very sorry being unable to identify the remindee. Could you give me another picture?",
        #                     "image": ""})
        # else:
        # under normal conditions, will initiate sageMaker processing job. 
        # The uploaded image will always be named as the same key and prefixed with user_id, and might replace the previous image
        image_bytes = await utils.normalize_file_format(file)
        user_id = user['sub']
        object_key = f"{user_id}/image.jpg"
        print("object_key get")
        try:
            s3_utils.s3_client.put_object(Bucket=config.S3_MODEL_WEIGHT_BUCKET_NAME, Key=object_key, Body=image_bytes, ContentType="image/jpeg")
        except Exception as e:
            raise HTTPException("error uploading to S3:", f"{e}")
        
        job_id = "job:" + str(uuid.uuid4())
        job = {
            "type": "inference",
            "user_id": user_id,
            "job_id": job_id,
            "status": "queued",
            "image_object_key": object_key,
            "created_at": int(time.time()),
            "expires_at": int(time.time()) + int(config.INFERENCE_TIME_OUT_SEC)
        }

        await queue_manager.cancel_jobs_by_user(user_id, "inference")
        await queue_manager.add_job(job)
        return ({"status": "queued", "job_id": job_id})

                
    except Exception as e:
        print("error:", e)
        raise HTTPException(400, f"{e}")
    


@router.get("/check-inference-status")
async def check_inference_status(job_id: str, user: Dict = Depends(congnito_auth.get_current_user), redis_client: redis.Redis = Depends(redis_utils.get_redis)):
    
    # if LOCAL_INFERENCE:
    #     inference_result = {}
    #     output_file = f"{local_inference.temp_dir}/{user['sub']}/result.json"
    #     if os.path.exists(output_file):
    #         with open(output_file, "r") as f:
    #             inference_result = json.load(f)
                
    #         return utils.ApiResponse(success=True,
    #                 message="Completed",
    #                 data={"person": inference_result['name'],
    #                     "summary": inference_result['ai_summary'],
    #                     "image": inference_result['image_url']})
                        
    #     else:
    #         return utils.ApiResponse(success=True,
    #             message="Completed",
    #             data={"person": "Cannot identify the face",
    #                 "summary": "Your AI assistant feels very sorry being unable to identify the remindee. Could you give me another picture?",
    #                 "image": ""})
    # else:
        # this part is only used for sageMaker
        # Download file from S3
    
    try:
        user_id = user['sub']
        object_key = f"{user_id}/result/inference/" + job_id
        # check if the key exists or not
        s3_utils.s3_client.head_object(Bucket = config.S3_MODEL_WEIGHT_BUCKET_NAME, Key=object_key)
        response = s3_utils.s3_client.get_object(Bucket=config.S3_MODEL_WEIGHT_BUCKET_NAME, Key=object_key)
        status = response['Body'].read().decode('utf-8')
        print("status:", status)
    
    except botocore.exceptions.ClientError as e:
        print("the inference job is in queueing status.")
        status = "queued"
    
    if "complete" in status:
        await redis_utils.redis_client.hset(job_id, "status", "complete")
        remindee_name = status.split(":")[1].strip()
        if remindee_name == "unknown":
            return {"status": "complete", "person": "unknown"}
        else:
            # remindee_name = "Catheline_zztxa"
            inference_result = LLM_utils.get_summary(user_id, remindee_name)
            return {"status": "complete", 
                    "person": remindee_name, 
                    "data": {"person": inference_result['name'],
                        "summary": inference_result['ai_summary'],
                        "image": inference_result['image_url']}
                    }
    elif "model-nonexist" in status:
        await redis_utils.redis_client.hset(job_id, "sattus", "abort") 
        return {"status": "model-nonexist", "person": None}
    
    # if the job is still pending or starts, but time has expired, then set status to abort
    expires_at_str = await redis_utils.redis_client.hget(job_id, "expires_at")

    if expires_at_str is not None:
        expires_at = int(expires_at_str)
    else:
        expires_at = None  # or handle missing case 
    
    print("expires_at:", expires_at)      
    if time.time() > expires_at and (status == "start" or status=="queued" or status=="idle"):
        await redis_utils.redis_client.hset(job_id, "sattus", "timeout") 
        return {"status": "timeout", "person": None}
             
    if status == "start":
        await redis_utils.redis_client.hset(job_id, "status", "start")
        return {"status": "start", "person": None}
    elif status == "abort":
        await redis_utils.redis_client.hset(job_id, "status", "abort")
        return {"status": "abort", "person": None}

    return {"status": "queued", "person": None}


# @router.get("/check-inference-status")
# def check_inference_status(job_id: str, user: Dict = Depends(congnito_auth.get_current_user)):
#     try:
#         if LOCAL_INFERENCE:
#             # for demo, simulate the time-consuming work
#             time.sleep(2)
#             return {"status": "Completed"}
#         else:
#             # for sageMaker inference
#             response = sagemaker_utils.sagemaker_client.describe_transform_job(TransformJobName=job_name)
#             status = response["TransformJobStatus"]
#             return {"status": status}
#     except Exception as e:
#         raise HTTPException(f"{e}")



@router.get("/check-training-status")
async def check_training_status(job_id: str, user: Dict = Depends(congnito_auth.get_current_user)):
    try:
        user_id = user['sub']
        object_key = f"{user_id}/result/train/" + job_id
        # check if the key exists or not
        s3_utils.s3_client.head_object(Bucket = config.S3_MODEL_WEIGHT_BUCKET_NAME, Key=object_key)
        
        response = s3_utils.s3_client.get_object(Bucket=config.S3_MODEL_WEIGHT_BUCKET_NAME, Key=object_key)
        status = response['Body'].read().decode('utf-8')
    
    except botocore.exceptions.ClientError as e:
        # if it could not get the object id on S3, assuming it is queueing
        print(f"could not find the {object_key} on S3. Might be in the queue.")
        status = "queued"
    
    # if the job is still pending or starts, but time has expired, then set status to abort
    expires_at_str = await redis_utils.redis_client.hget(job_id, "expires_at")

    if expires_at_str is not None:
        expires_at = int(expires_at_str)
    else:
        expires_at = None  # or handle missing case 
    
    if expires_at is None:
        status = "queued"
    elif time.time() > expires_at and (status == "start" or status=="queued" or status=="idle"):
        await redis_utils.redis_client.hset(job_id, "sattus", "timeout") 
        return {"status": "timeout"}
        
    if status == "complete":
        await redis_utils.redis_client.hset(job_id, "status", "complete")
        return {"status": "complete"}
    elif status == "start":
        await redis_utils.redis_client.hset(job_id, "status", "start")
        return {"status": "start"}
    elif status == "abort":
        await redis_utils.redis_client.hset(job_id, "status", "abort")
        return {"status": "abort"}
    elif status == "terminate":
        await redis_utils.redis_client.hset(job_id, "status", "terminate")
        return {"status": "terminate"}
    
    return {"status": "queued"}
    

@router.get("/train")
async def train(user: Dict = Depends(congnito_auth.get_current_user)):

    user_id = user['sub']
    job_id = "job:" + str(uuid.uuid4())
    job = {
        "type": "train",
        "user_id": user_id,
        "job_id": job_id,
        "created_at": int(time.time()),
        "expires_at": int(time.time()) + int(config.TRAINING_TIME_OUT_SEC)
    }
    
    await queue_manager.cancel_jobs_by_user(user_id, "train")
    await queue_manager.add_job(job)
    return {"status": "queued", "job_id": job_id}


@router.post("/upload")
async def upload_images(
    person_name: str = Form(...),
    relationship: str = Form(...),
    summary: List[str] = Form(),
    files: List[UploadFile] = File(...),
    db: Session = Depends(database.get_db),
    user: Dict = Depends(congnito_auth.get_current_user)):
    
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    try:
        for file, individual_summary in zip(files, summary):
            image_bytes = await utils.normalize_file_format(file)
            
            file_name = file.filename
            timestamp = int(time.time())
            unique_file_name = f"{timestamp}_{file_name}"
            user_id = user['sub']

            image_object_key = f"{user_id}/{person_name}/{unique_file_name}"
            res = s3_utils.upload_image_to_s3(image_object_key, image_bytes)

            # Store in PostgreSQL User_remindee table
            new_entry = database.UserRemindee(
                user_id=user['sub'],
                image_object_key=unique_file_name,
                person_name=person_name,
                relationship=relationship,
                summary=individual_summary
                # summary=summary
            )
            db.add(new_entry)
        db.commit()
        db.refresh(new_entry)
        
        relationship, accumulated_summary = LLM_utils.get_accumulated_descriptions_for_remindee(user_id, person_name)
        ai_summary, image_obj_key  = LLM_utils.generate_summary_for_remindee(user_id, person_name, relationship, accumulated_summary)
        # sometimes the LLM will generate strange comment
        image_obj_key = f"{user_id}/{person_name}/{image_obj_key}"
        presigned_url = s3_utils.get_image_url_from_s3(image_obj_key)['presigned_url']
        
        return utils.ApiResponse(success=True,
                message="images and info are saved to database.",
                data={"person": person_name,
                        "summary": ai_summary,
                        "image": presigned_url})
        
    except Exception as e:
        raise HTTPException(400, f"{e}")

 

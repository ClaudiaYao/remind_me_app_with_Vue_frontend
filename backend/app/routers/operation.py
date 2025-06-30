
from services import database
from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException
import asyncio
from typing import Dict, List
from sqlalchemy.orm import Session
from services import congnito_auth, s3_utils, sagemaker_utils, config 
from routers import utils
import time
from services import local_inference, LLM_utils
import os
import json


LOCAL_INFERENCE = True

router = APIRouter(
    prefix="/operation",
    tags=["operation"],
    responses={404: {"description": "Not found this API route."}},
)


@router.get("/is-model-exist")
async def is_model_exist(user: Dict = Depends(congnito_auth.get_current_user)):
    if sagemaker_utils.object_exists(config.S3_MODEL_WEIGHT_BUCKET_NAME, f"{user['sub']}/model.pth"):
        return {"status": True}
    return {"status": False}
    
@router.post("/identify")
async def identify(
    file: UploadFile = File(...),
    user: Dict = Depends(congnito_auth.get_current_user)):
    
    try:
        if not file:
            raise HTTPException(status_code=400, detail="No files uploaded")
        image_bytes = await file.read()
        user_id = user['sub']

        # for demo
        if LOCAL_INFERENCE:
            object_key = f"{user_id}/image.jpg"
            
            try:
                s3_utils.s3_model_client.put_object(Bucket=config.S3_MODEL_WEIGHT_BUCKET_NAME, Key=object_key, Body=image_bytes, ContentType="image/jpeg")
            except Exception as e:
                raise HTTPException("error uploading to S3:", f"{e}")
            
            summary = local_inference.local_inference(user_id, object_key)
            
            local_file_path = f"{local_inference.temp_dir}/{user_id}/result.json"
            if summary is None:
                return utils.ApiResponse(success=False,
                    message="model does not exist",
                    data=None)
                                
            elif isinstance(summary, dict):
                with open(local_file_path, "w") as f:
                    json.dump(summary, f, indent=4)
                
                return utils.ApiResponse(success=True,
                        message="Completed",
                        data={"person": summary['name'],
                            "summary": summary["ai_summary"],
                            "image": summary["image_url"]})
                
            elif isinstance(summary, str) and summary =="NA":
                if os.path.exists(local_file_path):
                    os.remove(local_file_path)
            
                return utils.ApiResponse(success=True,
                        message="Completed",
                        data={"person": "Cannot identify the face",
                            "summary": "Your AI assistant feels very sorry being unable to identify the remindee. Could you give me another picture?",
                            "image": ""})
        else:
        # under normal conditions, will initiate sageMaker processing job. 
        # The uploaded image will always be named as the same key and prefixed with user_id, and might replace the previous image
            object_key = "image.jpg"
            response_payload = sagemaker_utils.trigger_sagemaker_inference_job_new(user_id, object_key)
            return utils.ApiResponse(success=True,
                                message="Job submitted",
                                data=response_payload)
                
    except Exception as e:
        raise HTTPException(400, f"{e}")
    


@router.get("/get-inference-result")
async def get_inference_result(user: Dict = Depends(congnito_auth.get_current_user)):
    
    if LOCAL_INFERENCE:
        inference_result = {}
        output_file = f"{local_inference.temp_dir}/{user['sub']}/result.json"
        if os.path.exists(output_file):
            with open(output_file, "r") as f:
                inference_result = json.load(f)
                
            return utils.ApiResponse(success=True,
                    message="Completed",
                    data={"person": inference_result['name'],
                        "summary": inference_result['ai_summary'],
                        "image": inference_result['image_url']})
                        
        else:
            return utils.ApiResponse(success=True,
                message="Completed",
                data={"person": "Cannot identify the face",
                    "summary": "Your AI assistant feels very sorry being unable to identify the remindee. Could you give me another picture?",
                    "image": ""})
    else:
        # this part is only used for sageMaker
        # Download file from S3
        s3_utils.s3_client.download_file(config.S3_BUCKET_NAME, config.S3_DOWNLOAD_OUTPUT_FILE_KEY, "result.csv")
        with open("result.csv", "r") as f:
            result = f.readlines()
        return {"status": "Completed", "result": result}


@router.get("/check-inference-status")
def check_inference_status(job_name: str):
    try:
        if LOCAL_INFERENCE:
            # for demo, simulate the time-consuming work
            time.sleep(2)
            return {"status": "Completed"}
        else:
            # for sageMaker inference
            response = sagemaker_utils.sagemaker_client.describe_transform_job(TransformJobName=job_name)
            status = response["TransformJobStatus"]
            return {"status": status}
    except Exception as e:
        raise HTTPException(f"{e}")



@router.get("/check-training-status")
async def check_training_status(job_name: str, user: Dict = Depends(congnito_auth.get_current_user)):
    try:
        response = sagemaker_utils.sagemaker_client.describe_training_job(TrainingJobName=job_name)
        status = response['TrainingJobStatus']
        
        # clean up the output folder. 
        if status == "Completed":
            old_key = f"{user['sub']}/{job_name}/output/model.tar.gz"
            new_key = f"{user['sub']}/model.tar.gz"
            # create async task so that the endpoint could respond to user fast
            asyncio.create_task(sagemaker_utils.adjust_model_key(old_key, new_key))
        return {"status": status}
    except Exception as e:
        raise HTTPException(f"{e}")
    

@router.get("/train")
async def train(user: Dict = Depends(congnito_auth.get_current_user)):
    try:
        response_payload = sagemaker_utils.trigger_sagemaker_training_job(user['sub'])
        return utils.ApiResponse(success=True,
                            message="Job submitted",
                            data=response_payload)
            
    except Exception as e:
        raise HTTPException(400, f"{e}")


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
            image_bytes = await file.read()
            
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

 

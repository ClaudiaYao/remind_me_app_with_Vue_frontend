from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Query
from services import congnito_auth
from sqlalchemy.orm import Session
from services import database
from services import s3_utils, LLM_utils, config
from routers import utils
from services import redis_utils
import json
import redis.asyncio as redis
from services import database


router = APIRouter(
    prefix="/user",    
    tags=["user"],
    responses={404: {"description": "This API endpoint is not found."}},
)

@router.get("/login")
async def login(user: dict = Depends(congnito_auth.get_current_user), db: Session = Depends(database.get_db), redis_depend: redis.Redis = Depends(redis_utils.get_redis)):
    user_id = user['sub']
    
    user = db.query(database.UserSummary).filter(database.UserSummary.user_id == user_id).first()
    if not user:
        # 2. Insert new user
        new_user = database.UserSummary(user_id = user_id, nick_name = "HappyBird",  avatar_object_key = "default_profile2.png")
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

    await redis_utils.redis_client.expire(f"user:{user_id}", 3600)
    
    
    return utils.ApiResponse(
            success=True,
            message="user logins successfully")
    
@router.post("/logout")
async def logout(user: dict = Depends(congnito_auth.get_current_user), db: Session = Depends(database.get_db), redis_depend: redis.Redis = Depends(redis_utils.get_redis)):
    user_id = user['sub']
    await redis_utils.redis_client.expire(f"user:{user_id}", 300)
    
    return utils.ApiResponse(
            success=True,
            message="user logouts successfully")


@router.get("/profile")
async def get_profile(retrieve_new_profile: bool, skip: int=Query(0), limit: int=Query(5), user: dict = Depends(congnito_auth.get_current_user), 
                db: Session = Depends(database.get_db), 
                redis_depend: redis.Redis = Depends(redis_utils.get_redis)):
    try:
        """Fetch user profile from database"""
        user_id = user["sub"] 
        
        if not retrieve_new_profile:
            # retrieve the records from redis which match a certain pattern: remindee:<user_id>, and return those records to front end
            pattern = f"user:{user_id}:*"
            matching_keys = list(await redis_utils.redis_client.scan_iter(pattern))  # Get all matching keys

            if len(matching_keys) > 0:
                data = []
                for key in matching_keys:
                    value = await redis_utils.redis_client.get(key)  # Retrieve value from Redis
                    if value:
                        data.append(json.loads(value))  # Convert JSON string back to dictionary
            
                return utils.ApiResponse(
                success=True,
                message="User profile fetched successfully",
                data = {"remindee": data})
        
        # if no cache remindee data, retrieve from the Postgresql database
        if config.USE_POSTGRESQL==1:
            batch_remindees = db.query(database.UserRemindee)\
            .filter(database.UserRemindee.user_id == user_id)\
            .order_by(database.UserRemindee.person_name)\
            .distinct(database.UserRemindee.person_name)\
            .offset(skip)\
            .limit(limit+1)\
            .all()
        else:
            batch_remindees = db.query(database.UserRemindee)\
            .filter(database.UserRemindee.user_id == user_id)\
            .order_by(database.UserRemindee.person_name)\
            .group_by(database.UserRemindee.person_name)\
            .offset(skip)\
            .limit(limit+1)\
            .all()
        
        # intentionally fetch limit+1 records to check if there are more records after the current batch
        has_more = len(batch_remindees) > limit
    
        data = []
        if not batch_remindees:
             return utils.ApiResponse(
            success=False,
            message="could not load any remindee information. Add remindee first.",
            data = {"remindee": data, 
                    "has_more": False})
        
        
        for record in batch_remindees[:limit]:

            remindee = utils.map_to_remindee_profile_response(record)
            # S3 object key needs to combine user_id, person_name and the image file name together to form the final key in S3
            object_key = f"{user_id}/{record.person_name}/{record.image_object_key}"
            remindee.image_object_key = s3_utils.get_image_url_from_s3(object_key)['presigned_url']
            data.append(remindee)
            # get the remindee's LLM AI generated summary from table remindee_summary, and then save remindee info to Redis
            ai_summary = db.query(database.RemindeeSummary).filter(database.RemindeeSummary.user_id == user_id,
                                                                   database.RemindeeSummary.person_name==remindee.person_name).first()

            if ai_summary is None:
                remindee_name = record.person_name
                relationship, accumulated_summary = LLM_utils.get_accumulated_descriptions_for_remindee(user_id, remindee_name)
                remindee.ai_summary, _ = LLM_utils.generate_summary_for_remindee(user_id, remindee_name, relationship, accumulated_summary)

                
            else:
                remindee.ai_summary = ai_summary.summary
                
            # check redis cache data and set expiry
            user_redis_id = f"remindee:{user_id}:{record.person_name}"

            await redis_utils.redis_client.setex(user_redis_id, 2700, remindee.model_dump_json())
        
        return utils.ApiResponse(
            success=True,
            message="User profile fetched successfully",
            data = {"remindee": data, 
                    "has_more": has_more})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.get("/user-profile")
async def get_user_profile(user: dict = Depends(congnito_auth.get_current_user), 
                db: Session = Depends(database.get_db), 
                redis_depend: redis.Redis = Depends(redis_utils.get_redis)):
    try:
        """Fetch user profile from database"""
        user_id = user["sub"] 
        
        user_data = await redis_utils.redis_client.get(f"user:{user_id}")
        
        # if the user profile is not in Redis, get it from postgresql database and get presigned url for avatar image, then
        # save the user profile to Redis
        if user_data is None:
            db_user = db.query(database.UserSummary).filter(database.UserSummary.user_id == user_id).first()

            if not db_user:
                raise HTTPException(status_code=404, detail="User profile not found")

            avatar_url = s3_utils.get_image_url_from_s3(f"avatar/{db_user.avatar_object_key}")['presigned_url']
            
            user_data = {"user_summary": utils.map_to_user_profile_response(db_user),
                        "email": user['email'],
                        "avatar_url": avatar_url}
            
            redis_user_data = {"user_summary": utils.map_to_user_profile_response(db_user).model_dump_json(),
                        "email": user['email'],
                        "avatar_url": avatar_url}
            await redis_utils.redis_client.setex(f"user:{user_id}", 2700, json.dumps(redis_user_data))
        else:
            # If user profile is in Redis, load info from Redis
            parsed_data = json.loads(user_data)
            user_summary_obj = utils.UserSummaryUpdate.model_validate_json(parsed_data["user_summary"])
            
            user_data = {
            "user_summary": user_summary_obj,
            "email": parsed_data["email"],
            "avatar_url": parsed_data["avatar_url"]
            }
               
        return utils.ApiResponse(
                success=True,
                message="User profile fetched successfully",
                data = user_data)
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/update-profile")
async def update_user_profile(nick_name: str = Form(...),
                        description: str = Form(...),
                        age: int = Form(...),
                        phone_number: str = Form(...),
                         user: dict = Depends(congnito_auth.get_current_user), 
                         avatar: UploadFile = File(None),
                         db: Session = Depends(database.get_db),
                         redis_depend: redis.Redis = Depends(redis_utils.get_redis)):
    
    try: 
        user_id = user["sub"]
        
        db_user = db.query(database.UserSummary).filter(database.UserSummary.user_id == user_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        if nick_name is not None:
            setattr(db_user, "nick_name", nick_name)
        
        if description is not None:
            setattr(db_user, "description", description)
            
        if age is not None:
            setattr(db_user, "age", age)
            
        if phone_number is not None:
            setattr(db_user, "phone_number", phone_number)
            
        if avatar:
            try:
                # Create the file name for the image
                file_name = f"{user_id}.{avatar.filename.split('.')[-1]}"
                image_bytes = await avatar.read()
                
                s3_utils.upload_image_to_s3(
                    f"avatar/{file_name}", 
                    image_bytes)  
                
                db_user.avatar_object_key = file_name
            
            except Exception as e:
                raise HTTPException(status_code=500, detail="Error uploading image to S3")
        
        db.commit()
        # db.refresh(db_user)
        
        # to avoid unconsistent information, delete the user info from Redis
        await redis_utils.redis_client.delete(f"user:{user_id}")
        return utils.ApiResponse(
            success=True,
            message="User profile updated successfully")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



@router.delete("/delete_remindee")
async def delete_remindee(
    person_name: str,
    db: Session = Depends(database.get_db),
    user: dict = Depends(congnito_auth.get_current_user)):
    
    user_id = user['sub']
    if person_name == "":
        return utils.ApiResponse(success=False,
                message="remindee name should not be empty.",
                data=None)
        
    try:
        # Step 1: Filter matching remindee records
        remindees = db.query(database.UserRemindee).filter_by(user_id=user_id, person_name=person_name).all()

        if not remindees:
            return utils.ApiResponse(success=False,
                message="remindee name does not exist.",
                data=None)

        # Step 2: Extract image object keys
        image_obj_keys = [r.image_object_key for r in remindees if r.image_object_key]

        # Step 3: Convert image URLs to S3 keys and delete from S3
        for image_obj_key in image_obj_keys:
            s3_utils.s3_image_client.delete_object(Bucket=config.S3_IMAGE_STORAGE_BUCKET_NAME, Key=f"{user_id}/{person_name}/{image_obj_key}")

        # Step 4: Delete records from DB (this will also cascade delete RemindeeSummary)
        for r in remindees:
            db.delete(r)
        
        # the remindee might have the possiblity not having Ai summary yet
        remindee_summary = db.query(database.RemindeeSummary).filter_by(user_id=user_id, person_name=person_name).first()
        if remindee_summary:
            db.delete(remindee_summary)
            
        db.commit()
        return utils.ApiResponse(success=True,
            message="All the records of the remindee have been cleared.",
            data=None)

    except Exception as e:
         raise HTTPException(status_code=400, detail=str(e))
    
    

@router.get("/remindee_info")
async def display_remindee_info(
    person_name: str,
    db: Session = Depends(database.get_db),
    user: dict = Depends(congnito_auth.get_current_user)):
    
    user_id = user['sub']
    if person_name == "":
        return utils.ApiResponse(success=False,
                message="remindee name should not be empty.",
                data=None)
        
    try:
        # Step 1: Filter matching remindee records
        remindee_records = db.query(database.UserRemindee).filter_by(user_id=user_id, person_name=person_name).all()

        if not remindee_records:
            return utils.ApiResponse(success=False,
                message="remindee name does not exist.",
                data=None)


        records = []
        image_presigned_url = {}
        for remindee_record in remindee_records:
            img_obj_key = remindee_record.image_object_key
            
            print(remindee_record.image_object_key, remindee_record.person_name, remindee_record.summary, remindee_record.relationship)
        
            record = utils.UserRemindee(image_object_key=img_obj_key, 
                                        person_name=remindee_record.person_name,
                                        summary=remindee_record.summary,
                                        relationship=remindee_record.relationship)
            presigned_url = s3_utils.get_image_url_from_s3(f"{user_id}/{person_name}/{img_obj_key}")['presigned_url']
            image_presigned_url[img_obj_key] = presigned_url
            records.append(record)
        
        # the remindee might have the possiblity not having Ai summary yet
        remindee_summary = db.query(database.RemindeeSummary).filter_by(user_id=user_id, person_name=person_name).first()
        ai_summary = ""
        if remindee_summary:
            ai_summary = remindee_summary.summary
        
        remindee_info = utils.RemindeeInfoAll(records=records, ai_summary=ai_summary, image_presigned_url=image_presigned_url)
            
        return utils.ApiResponse(success=True,
            message="All the records of the remindee have been returned.",
            data=remindee_info)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    
@router.post("/change_remindee_info")
async def change_remindee_info(
    remindee_data_changes: utils.RemindeePayload,
    db: Session = Depends(database.get_db),
    user: dict = Depends(congnito_auth.get_current_user)):
    
    user_id = user['sub']
    if remindee_data_changes is None:
        return utils.ApiResponse(success=False,
                message="no remindee information",
                data=None)
        
    try:
        for remindee_upt_record in remindee_data_changes.items:
            person_name = remindee_data_changes.person_name
            image_object_url = remindee_upt_record.image_object_url
            record = db.query(database.UserRemindee).filter_by(user_id=user_id, 
                                                            person_name=person_name, 
                                                            image_object_key=image_object_url).first()
            
            if record:
                if remindee_upt_record.action == "delete":
                    # delete the image on the S3
                    s3_utils.s3_client.delete_object(Bucket=config.S3_IMAGE_STORAGE_BUCKET_NAME, Key=f"{user_id}/{person_name}/{image_object_url}")
                    
                    print("deleted from s3")
                    # delete the record in database
                    db.delete(record)
                    
                elif remindee_upt_record.action == "update":
                    record.summary = remindee_upt_record.image_summary
            
                db.commit()
        return utils.ApiResponse(success=True,
            message="All the records of the remindee have been updated.",
            data=None)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
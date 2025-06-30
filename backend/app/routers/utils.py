
from pydantic import BaseModel
from services import database
from typing import Any, List

# Front end uses the model to update profile
class UserSummaryUpdate(BaseModel):
    nick_name: str | None = None
    description: str | None = None
    age: int | None = None
    phone_number: str | None = None

# Front end uses the model to update profile
class UserRemindee(BaseModel):
    image_object_key: str
    person_name: str
    summary:str | None = None
    relationship: str
    ai_summary: str | None = None
    
# response wrapper
class ApiResponse(BaseModel):
    success: bool  # Indicates if the request was successful or not
    message: str | None = None  # Optional message for success or error
    data: Any| None = None  # Actual response data
    error_code: int | None = None  # Optional error code for detailed error tracking

class RemindeeInfoAll(BaseModel):
    records: List[UserRemindee] | None = None 
    ai_summary: str | None = None 
    image_presigned_url: dict | None = None


class RemindeeInfoUpdate(BaseModel):
    image_object_url: str | None = None
    image_summary: str | None = None    
    action: str | None = None   # "delete" or "update"
    
class RemindeePayload(BaseModel):
    person_name: str
    items: List[RemindeeInfoUpdate]
    
# a customized response data
def map_to_user_profile_response(db_user: database.UserSummary):
    return UserSummaryUpdate(
        nick_name=db_user.nick_name if db_user.nick_name is not None else None,
        description= db_user.description if db_user.description is not None else None,
        age=db_user.age if db_user.age is not None else None,
        phone_number=db_user.phone_number if db_user.phone_number is not None else None)
    
# a customized response data
def map_to_remindee_profile_response(db_remindee: database.UserRemindee):
    return UserRemindee(
        image_object_key=db_remindee.image_object_key,
        person_name= db_remindee.person_name,
        summary=db_remindee.summary if db_remindee.summary is not None else None,
        relationship=db_remindee.relationship)
    

import boto3
import random
from app.services import config 

s3_client = boto3.client("s3", 
                         aws_access_key_id= config.S3_ACCESS_KEY_ID,
                         aws_secret_access_key= config.S3_SECRET_ACCESS_KEY,
                         region_name=config.AWS_REGION)

'''

d96a955c-b061-7080-194e-7e597383cad9: enquiry@thecodingfun.com

d9aa357c-20d1-704c-3877-63edc40201bd: claudia.yao2012@gmail.com

c9da252c-9041-7089-170c-be754918cc8d: e1331095@u.nus.edu

'''

# random_user_ids = ['097a558c-5001-70c9-19e0-284519f32472', 
#                    '196a354c-7001-708e-0404-b1278f580d20',
#                    '89eab5fc-4041-7070-5e1f-895b3e6c4ed6',
#                    '99dad5dc-9011-7084-c614-c1cae4051e30']
# person_names=["Shala", "Tera", "Draren", "Catheline", "David Chan", "Sandra Wong"]
summary = ["at the birthday party", "goint outside for dinner", "particiate in the wedding", "watch movie together", "have the afternoon tea", "visit you at the festival", 
           "just enjoy the time", "walk in the park", "meet on the street", "classmate in secondary school", "university rootmate"]
relationship = ['close friend', "daughter", "son", "best friend", "neighbour", "colleague", "doctor", "nurse", "friend", "caregiver"]
stored_persons = {}


bucket_name = config.S3_IMAGE_STORAGE_BUCKET_NAME

def list_s3_objects(bucket_name):
    # Initialize an empty list to hold object keys and URLs
    result = ""

    # Use the list_objects_v2 API to retrieve object keys
    response = s3_client.list_objects_v2(Bucket=bucket_name)
    
    if 'Contents' in response:
    # # If there are more objects, use the pagination token to fetch the next batch
    # while response.get('IsTruncated'):  # Check if there are more results
    #     response = s3_client.list_objects_v2(Bucket=bucket_name, ContinuationToken=response['NextContinuationToken'])
        # random_user = random.choice(random_user_ids)
        # random_name = random.choice(person_names)
        # random_relation = random.choice(relationship)
        
        for obj in response['Contents']:
            object_key = obj['Key']
            person_code = object_key.rsplit("/", 1)[0]
            user_id = object_key.split("/")[0]
            remindee_name = object_key.split("/")[1]
            object_file_name = object_key.split("/")[2]
            
            if person_code in stored_persons:
                # use existing relationship between the remindee and user
                remindee_relation = stored_persons[person_code]
                # the system accepts multiple relationship between remindee and user, so have a minor chance to add new relationship
                if random.randint(0, 5) == 5:
                    remindee_relation = random.choice(relationship)
            else:
                remindee_relation = random.choice(relationship)
                stored_persons[person_code] = remindee_relation
            
            if result != "":
                result += ",\n"
            
            random_summary = random.choice(summary)
            result += f"('{user_id}', '{object_file_name}', '{remindee_name}', '{random_summary}', '{remindee_relation}')"
            
        result += ";"

    return result

# The printed out result will be used to fill in the postfresql user_remindee table by using sql statement like this:
'''  
INSERT INTO user_remindee (user_id, image_object_key, person_name, summary, relationship) 
VALUES 
    (1, 'Alice', 'alice@example.com'),
    (2, 'Bob', 'bob@example.com'),
    (3, 'Charlie', 'charlie@example.com');    (replace VALUES with the printed result!!)

'''
res = list_s3_objects(bucket_name)
print(res)



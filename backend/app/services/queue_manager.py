
from services import redis_utils

async def add_job(job: dict):

    await redis_utils.redis_client.hset(job['job_id'], mapping=job)
    await redis_utils.redis_client.expire(job['job_id'], 600)  # auto-delete after 1 hour
    await redis_utils.redis_client.rpush("job_queue", job['job_id'])

async def cancel_jobs_by_user(user_id: str, job_type: str):
    # SCAN is better than KEYS for production (doesn't block Redis)
    cursor = 0
    while True:
        cursor, keys = await redis_utils.redis_client.scan(cursor=cursor, match="job:*")  # adjust prefix if jobs have one
        for job_id in keys:
            job = await redis_utils.redis_client.hgetall(job_id)
            if not job:
                # if job is None, it means this job does not exist in hash table or it has expired and gets deleted by Redis
                continue

            # If this job belongs to the user, update its status
            if job.get("user_id") == str(user_id) and job.get("type") == job_type:
                await redis_utils.redis_client.hset(job_id, "status", "cancelled")
                print(f"Cancelled {job_type} job {job_id} for user {user_id}")

        if cursor == 0:
            break
        

async def get_next_job():

    job_id = await redis_utils.redis_client.lpop("job_queue")
    if not job_id:
        return

    job_data = await redis_utils.redis_client.hgetall(job_id)
    
    if job_data.get("status") == "cancelled" or job_data.get("status") == "timeout":
        print(f"Skipping cancelled or timeout job: {job_data['job_id']}")
        return
    
    return job_data if job_data else None



from services import redis_utils

async def add_job(job: dict):
    
    await redis_utils.redis_client.hset(job['job_id'], mapping=job)
    await redis_utils.redis_client.rpush("job_queue", job['job_id'])


async def get_next_job():

    job_id = await redis_utils.redis_client.lpop("job_queue")
    if not job_id:
        return

    job_data = await redis_utils.redis_client.hgetall(job_id)
    
    if job_data.get("status") == "cancelled" or job_data.get("status") == "timeout":
        print(f"Skipping cancelled or timeout job: {job_data['job_id']}")
        return
    
    return job_data if job_data else None


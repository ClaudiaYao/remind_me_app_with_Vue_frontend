
import httpx
from services import config, redis_utils

if not config.RUNPOD_URL:
    raise ValueError("Missing value for secret_ai in .env")

async def is_idle():
    
    async with httpx.AsyncClient() as client:
        if (config.RUNPOD_URL[-1] == "/"):
            config.RUNPOD_URL = config.RUNPOD_URL[:-1]
        
        try:
            resp = await client.get(f"{config.RUNPOD_URL}/status")
            print("run_pod status:", resp.json().get("state"))
            return resp.json().get("state")=="idle"
        except Exception as e:
            print("the Runpod might not be turned on. ", e)
            return False
    

async def submit_job(job: dict):
    headers = {
        "x-api-key": config.API_KEY
    }        
        
    async with httpx.AsyncClient(follow_redirects=True) as client:
        try: 
            await redis_utils.redis_client.hset(job['job_id'], "status", "start")
            if job["type"] == "train":
                print("Submitting training job to runpod:", job)
                response = await client.post(f"{config.RUNPOD_URL}/train/", json=job, headers=headers)
            elif job["type"] == "inference":
                print("Submitting inference job to runpod:", job)
                response = await client.post(f"{config.RUNPOD_URL}/inference/", json=job, headers=headers)
            else:
                raise ValueError("Unknown job type")

            print("✅ Response status:", response.status_code)
            return True

        except httpx.RequestError as e:
            print(f"❌ Request to gpu_worker failed: {e}")
            return {"status": "error", "message": str(e)}
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return {"status": "error", "message": str(e)}

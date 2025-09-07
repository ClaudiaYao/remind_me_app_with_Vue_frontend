from fastapi import FastAPI
import uvicorn
import sys
from fastapi.middleware.cors import CORSMiddleware
from routers import operation, user
from contextlib import asynccontextmanager
import ssl
import certifi
from services import runpod_client, queue_manager, redis_utils, config
import asyncio
import redis.asyncio as redis
from  services import config

ssl_context = ssl.create_default_context(cafile=certifi.where())

host = "localhost"
port = 8001

origins = [
    "capacitor://localhost",  # Capacitor apps
    "http://localhost:5173",
]

if config.FRONTEND_URL_S3:
    origins.append(config.FRONTEND_URL_S3)
if config.RUNPOD_URL:
    origins.append(config.RUNPOD_URL)

async def job_scheduler():
    print("start job schedular...")
    while True:
        if await runpod_client.is_idle():  # check RunPod idle
            job = await queue_manager.get_next_job()  # get from Redis or memory
            if job:
                await runpod_client.submit_job(job)
                
        await asyncio.sleep(2)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await redis_utils.redis_client.ping()
        print("✅ Connected to Redis")
        await redis_utils.redis_client.close()  # Close the connection when done
    except redis_utils.redis_client.ConnectionError:
        print("❌ Redis not available at startup, Are you sure that redis server is running? use redis-sererve command to start redis server")
        sys.exit(1)

    # ✅ Job loop background task
    app.state.job_task = asyncio.create_task(job_scheduler())
    print("🚀 Job loop started")
    
    yield
    try:
        await redis_utils.redis_client.ping()
        print("🔌 Closing Redis connection...")
        await redis_utils.redis_client.close()  # Do NOT use await here
        await redis_utils.redis_client.connection_pool.disconnect()  # Do NOT use await here
        print("✅ Redis connection closed")
    except redis.ConnectionError:
        print("⚠️ Redis already disconnected or unreachable")
        
    # ✅ Cancel job loop task
    app.state.job_task.cancel()
    print("🛑 Job loop task cancelled")
        
    
    
app = FastAPI(title="Remind-Me API", description="API Documentation", version="0.0.1", lifespan=lifespan)
app.include_router(user.router)
app.include_router(operation.router)


# ✅ Allow requests from React frontend (localhost:5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 🔥 Update this to match your frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # ✅ Allow all HTTP methods (POST, GET, DELETE, etc.)
    allow_headers=["*"],  # ✅ Allow all headers
)



@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI!"}

if __name__ == "__main__":
    uvicorn.run(app, host=host, port=port)


# run: 
# uvicorn main:app --reload
# uvicorn main:app --host localhost --port 8001 --reload
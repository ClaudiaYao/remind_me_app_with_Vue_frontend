from fastapi import FastAPI
import uvicorn
import sys
from fastapi.middleware.cors import CORSMiddleware
from routers import operation
from routers import user
import redis
from contextlib import asynccontextmanager
import ssl
import certifi

ssl_context = ssl.create_default_context(cafile=certifi.where())


host = "localhost"
port = 8000
# redis_client: redis.Redis | None = None

origins = [
    # "http://remind-me-frontend.s3-website-ap-southeast-1.amazonaws.com",
    "http://localhost:8000",
    # "https://3.0.1.90:8000",
    "capacitor://localhost",  # Capacitor apps
    "http://localhost:5173",
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)     
    try:
        redis_client.ping()
        print("✅ Connected to Redis")
        redis_client.close()  # Close the connection when done
    except redis.ConnectionError:
        print("❌ Redis not available at startup, Are you sure that redis server is running? use redis-sererve command to start redis server")
        sys.exit(1)
        
    yield
    try:
        redis_client.ping()
        print("🔌 Closing Redis connection...")
        redis_client.close()  # Do NOT use await here
        redis_client.connection_pool.disconnect()  # Do NOT use await here
        print("✅ Redis connection closed")
    except redis.ConnectionError:
        print("⚠️ Redis already disconnected or unreachable")
        
    
    
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

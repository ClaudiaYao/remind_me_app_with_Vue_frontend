import redis.asyncio as redis
from contextlib import asynccontextmanager
from services import config
# Dependency for Database Session
# Initialize Redis connection globally

redis_client = redis.Redis(host=config.REDIS_HOST, port=6379, decode_responses=True)

@asynccontextmanager
def get_redis():
    redis_client = redis.Redis(host=config.REDIS_HOST, port=6379, db=0, decode_responses=True)
    
    try:
        yield redis_client  # Provide the Redis instance
    finally:
        redis_client.close()  # Close the connection when done

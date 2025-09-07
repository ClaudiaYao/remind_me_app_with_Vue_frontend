# import redis.asyncio as redis
# from contextlib import asynccontextmanager
# from services import config
# # Dependency for Database Session
# # Initialize Redis connection globally

# redis_client = redis.Redis(host=config.REDIS_HOST, port=6379, decode_responses=True)

# @asynccontextmanager
# def get_redis():
#     redis_client = redis.Redis(host=config.REDIS_HOST, port=6379, db=0, decode_responses=True)
    
#     try:
#         yield redis_client  # Provide the Redis instance
#     finally:
#         redis_client.close()  # Close the connection when done


import redis.asyncio as redis
from contextlib import asynccontextmanager
from services import config

# Create a single global Redis connection (connection pool)
redis_client = redis.Redis(
    host=config.REDIS_HOST,
    port=6379,
    db=0,
    decode_responses=True
)

@asynccontextmanager
async def get_redis():
    try:
        yield redis_client  # Reuse global client
    finally:
        # Optionally close if you want to teardown the app
        # await redis_client.close()
        pass

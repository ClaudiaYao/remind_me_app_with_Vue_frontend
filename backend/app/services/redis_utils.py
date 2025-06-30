import redis
import json

# Dependency for Database Session
# Initialize Redis connection globally
def get_redis():
    redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
    try:
        yield redis_client  # Provide the Redis instance
    finally:
        redis_client.close()  # Close the connection when done

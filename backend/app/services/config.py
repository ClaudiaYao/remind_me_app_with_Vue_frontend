import os
from dotenv import load_dotenv

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION")

S3_ACCESS_KEY_ID = os.getenv("S3_ACCESS_KEY_ID")
S3_SECRET_ACCESS_KEY = os.getenv("S3_SECRET_ACCESS_KEY")

# AWS S3 for image storage
S3_IMAGE_STORAGE_BUCKET_NAME = os.getenv("S3_IMAGE_STORAGE_BUCKET_NAME")
# AWS S3 for model weight storage
S3_MODEL_WEIGHT_BUCKET_NAME = os.getenv("S3_MODEL_WEIGHT_BUCKET_NAME")

# S3_BUCKET = "my-saas-app-images"
SAGEMAKER_ROLE_ARN = os.getenv("SAGEMAKER_ROLE_ARN")

# Postgresql AWS
DATABASE_ADMIN_NAME = os.getenv("DATABASE_ADMIN_NAME")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DB_INSTANCE = os.getenv("DB_INSTANCE")
DATABASE_NAME = os.getenv("DATABASE_NAME")
DATABASE_PORT = os.getenv("DATABASE_PORT")

# toggle between postgresql and sqlite
# DATABASE_URL = f"postgresql://{DATABASE_ADMIN_NAME}:{DATABASE_PASSWORD}@{DB_INSTANCE}:{DATABASE_PORT}/{DATABASE_NAME}"
DATABASE_URL = "sqlite:///./dev.sqlite3"

# Cognito AWS
COGNITO_USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID")
COGNITO_APP_CLIENT_ID = os.getenv("COGNITO_APP_CLIENT_ID")

# URL to fetch public Cognito keys
COGNITO_ISSUER = f"https://cognito-idp.{AWS_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}"
JWT_KEYS_URL = f"{COGNITO_ISSUER}/.well-known/jwks.json"

LLM_MODEL_KEY = os.getenv("LLM_MODEL_KEY")

USE_POSTGRESQL=os.getenv("USE_POSTGRESQL")


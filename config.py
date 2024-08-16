import os
from dotenv import load_dotenv
from pydantic import BaseModel
import bcrypt

load_dotenv()

class Settings(BaseModel):
    twilio_account_sid: str = os.getenv('TWILIO_ACCOUNT_SID')
    twilio_auth_token: str = os.getenv('TWILIO_AUTH_TOKEN')
    
    pinecone_api_key: str = os.environ.get("PINECONE_API_KEY")
    pinecone_index: str = os.environ.get("PINECONE_INDEX")
    pinecone_namespace: str = os.environ.get("PINECONE_NAMESPACE")

    openai_api_key: str = os.getenv("OPENAI_API_KEY")
    openai_model_name: str = os.environ.get("GPT_MODEL")

    mongo_uri: str = os.environ.get("MONGO_URL")

    stripe_api_key: str = os.environ.get("STRIPE_API_KEY")

    authjwt_secret_key: str = os.environ.get("JWT_SECRET_KEY")
    salt_str: str = os.environ.get("JWT_SALT_BYTE")
    salt: bytes = bcrypt.gensalt()

CONFIG = Settings()
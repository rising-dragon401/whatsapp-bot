from decouple import config
from pydantic import BaseModel

class Settings(BaseModel):
    twilio_account_sid: str = config('TWILIO_ACCOUNT_SID')
    twilio_auth_token: str = config('TWILIO_AUTH_TOKEN')
    
    pinecone_api_key: str = config("PINECONE_API_KEY")
    pinecone_index: str = config("PINECONE_INDEX")
    pinecone_namespace: str = config("PINECONE_NAMESPACE")

    openai_api_key: str = config("OPENAI_API_KEY")
    openai_model_name: str = config("GPT_MODEL")

    mongo_uri: str = config("MONGO_URL")

    stripe_api_key: str = config("STRIPE_API_KEY")

    authjwt_secret_key: str = config("JWT_SECRET_KEY")
    salt: bytes = config("SALT").encode()

CONFIG = Settings()
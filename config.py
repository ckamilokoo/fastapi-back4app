from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    watsonx_api_key: str
    watsonx_project_id: str
    watsonx_url: str
    watsonx_model_id: str 
    SUPABASE_URL:str
    SUPABASE_KEY:str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
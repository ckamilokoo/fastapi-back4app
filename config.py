from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    watsonx_api_key: str
    watsonx_project_id: str
    watsonx_url: str
    watsonx_model_id: str = "meta-llama/llama-3-3-70b-instruct"  # Valor por defecto

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
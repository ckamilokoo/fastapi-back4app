from config import settings
from supabase import create_client, Client
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt  # Manejo de JWT para la autenticación
from passlib.context import CryptContext  # Encriptación de contraseñas
from datetime import datetime, timedelta, timezone

supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


# Esquema OAuth2 para manejar autenticación mediante tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Configuración de seguridad
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Duración del token en minutos


# Contexto para manejar la encriptación de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



# Dependencia para inyectar la base de datos en las funciones
# Función para crear token JWT
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Función para encriptar contraseñas
def get_password_hash(password: str):
    return pwd_context.hash(password)
from fastapi import APIRouter , HTTPException , status , Depends
from esquemas import Token , UserCreate , LoginRequest
from configuracion import supabase , get_password_hash , create_access_token , pwd_context , ALGORITHM , oauth2_scheme , SECRET_KEY
from jose import JWTError, jwt  # Manejo de JWT para la autenticación


router = APIRouter()

@router.post("/register", response_model=Token)
async def register_user(user: UserCreate):
    # Verificar si el usuario ya existe
    existing_user = supabase.table("users").select("username").eq("username", user.username).execute()
    if existing_user.data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El nombre de usuario ya está en uso.")

    # Hashear la contraseña y crear usuario en Supabase
    hashed_password = get_password_hash(user.password)
    response = supabase.table("users").insert({
        "username": user.username,
        "hashed_password": hashed_password,
        "rol": user.rol,
        "is_active": True
    }).execute()
    
    print(response)  # Para depuración
    
    # ⚠️ Validación corregida: Verificar si `data` está vacío
    if not response.data:
        raise HTTPException(status_code=500, detail="Error al crear el usuario.")

    # Generar token
    access_token = create_access_token({"sub": user.username})

    return {"access_token": access_token, "token_type": "bearer","user": {  # Agregar los datos del usuario aquí
            "id": response.data[0]["id"],
            "username": response.data[0]["username"],
            "is_active": response.data[0]["is_active"],
            "rol": response.data[0]["rol"]
        }}



# Login de usuario
@router.post("/token", response_model=Token)
async def login_for_access_token(login_request: LoginRequest):
    print(login_request.username)
    response = supabase.table("users").select("*").eq("username", login_request.username).execute()
    print(response)
    if not response.data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado.")

    user = response.data[0]
    if not pwd_context.verify(login_request.password, user["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Contraseña incorrecta.")

    access_token = create_access_token({"sub": user["username"]})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "username": user["username"],
            "rol": user["rol"],
            "is_active": user["is_active"],
        }
    }

@router.get("/users/me/")
async def read_users_me(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido."
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise credentials_exception
    except JWTError:  # ✅ Se usa JWTError en vez de PyJWTError
        raise credentials_exception

    response = supabase.table("users").select("*").eq("username", username).execute()
    if not response.data:
        raise credentials_exception

    user = response.data[0]
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "username": user["username"],
            "rol": user["rol"],
            "is_active": user["is_active"],
        }
    }


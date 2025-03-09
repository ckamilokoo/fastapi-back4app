import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
import joblib


modelo = joblib.load("./datos_ml/modelo.pkl")

# Función para hacer predicciones
def predecir_subsidio(datos):
    # Mapeo de RSH
    mapeo_rsh = {"0-40": 1, "41-60": 2, "61-70": 3, "71-80": 4, "81-90": 5}
    datos['RSH'] = mapeo_rsh.get(datos['RSH'], None)

    # Convertir los datos a DataFrame
    df_nuevo = pd.DataFrame([datos])

    # Asegurar que los campos numéricos sean del tipo correcto
    df_nuevo['monto_ahorro'] = float(df_nuevo['monto_ahorro'])
    df_nuevo['ingreso_mensual'] = float(df_nuevo['ingreso_mensual'])

    # Hacer la predicción
    prediccion = modelo.predict(df_nuevo)

    return prediccion[0]





import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
import joblib


ruta = 'backend/app/datos_ml/int_quesubsidio.csv'
# Supongamos que este es tu DataFrame original con muchas columnas
df = pd.read_csv(ruta)

# Seleccionar únicamente las columnas de interés
#df_modelo = df[['subsidio','RSH', 'tiene_ahorro','moneda_ahorro', 'zona_interes','monto_ahorro','ingreso_mensual','cant_integrante','limite_renta_1',	'limite_renta_2',	'limite_renta_3',	'limite_renta_4',	'limite_rm_renta_1',	'limite_rm_renta_2',	'limite_rm_renta_3',	'limite_rm_renta_4',	'limite_renta_1_ds19',	'limite_renta_2_ds19',	'limite_renta_3_ds19',	'limite_renta_4_ds19',	'limite_rm_renta_1_ds19',	'limite_rm_renta_2_ds19',	'limite_rm_renta_3_ds19',	'limite_rm_renta_4_ds19']]
df_modelo = df[['subsidio','RSH', 'tiene_ahorro','moneda_uf', 'zona_interes','monto_ahorro','ingreso_mensual','cant_integrante']]

mapeo_rsh = {"0-40":1,"41-60": 2, "61-70": 3, "71-80": 4, "81-90": 5}
df_modelo['RSH'] = df_modelo['RSH'].map(mapeo_rsh)

df_modelo.loc[:, 'monto_ahorro'] = df_modelo['monto_ahorro'].str.replace('.', '').str.replace(',', '.').astype(float)
df_modelo.loc[:, 'ingreso_mensual'] = df_modelo['ingreso_mensual'].str.replace('.', '').str.replace(',', '.').astype(float)


# Separar características (X) y variable objetivo (y)
X = df_modelo[['RSH', 'tiene_ahorro','moneda_uf', 'zona_interes','monto_ahorro','ingreso_mensual','cant_integrante']]
y = df_modelo['subsidio']

# Dividir los datos en entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Crear y entrenar el modelo (por ejemplo, un árbol de decisión)
modelo = DecisionTreeClassifier()
modelo.fit(X_train, y_train)

#almacenar el modelo
joblib.dump(modelo, "modelo.pkl")




# Hacer predicciones en el conjunto de prueba
y_pred = modelo.predict(X_test)

# Evaluar el modelo (ejemplo: precisión)
from sklearn.metrics import accuracy_score
precision = accuracy_score(y_test, y_pred)
print(f"Precisión del modelo: {precision}")

# Matriz de confusión
from sklearn.metrics import confusion_matrix
matriz_confusion = confusion_matrix(y_test, y_pred)
print(f"Matriz de confusión:\n{matriz_confusion}")

# Reporte de clasificación
from sklearn.metrics import classification_report
reporte_clasificacion = classification_report(y_test, y_pred)
print(f"Reporte de clasificación:\n{reporte_clasificacion}")
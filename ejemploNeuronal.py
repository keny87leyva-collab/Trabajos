# =============================================
# PROYECTO DE RED NEURONAL PARA PREDICCIÓN DE VENTAS
# =============================================

# 1️⃣ Importar librerías necesarias
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
import matplotlib.pyplot as plt

# 2️⃣ Cargar el dataset
# Asegúrate de que el archivo esté en la misma carpeta que este script
data = pd.read_csv("amazon_sales_2025_INR.csv")

# 3️⃣ Ver las primeras filas del dataset
print(data.head())

# 4️⃣ Verificar si hay valores nulos
print("\nValores nulos por columna:\n", data.isnull().sum())

# 5️⃣ Rellenar o eliminar nulos según convenga
data = data.dropna()

# 6️⃣ Seleccionar las columnas relevantes para el modelo
# Variables predictoras (X) y variable objetivo (y)
X = data[['Quantity', 'Unit_Price_INR', 'Review_Rating']]  # puedes agregar más
y = data['Total_Sales_INR']

# 7️⃣ Escalar los datos numéricos (para que la red aprenda mejor)
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)

# 8️⃣ Dividir los datos en entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# 9️⃣ Crear el modelo de red neuronal
model = Sequential([
    Dense(64, input_dim=X_train.shape[1], activation='relu'),  # capa de entrada
    Dense(32, activation='relu'),  # capa oculta
    Dense(1, activation='linear')  # salida (regresión)
])

# 10️⃣ Compilar el modelo
model.compile(optimizer='adam', loss='mean_squared_error', metrics=['mae'])

# 11️⃣ Entrenar la red neuronal
history = model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=100, batch_size=16, verbose=1)

# 12️⃣ Evaluar el modelo
loss, mae = model.evaluate(X_test, y_test)
print(f"\nPérdida (MSE): {loss:.2f}")
print(f"Error absoluto medio (MAE): {mae:.2f}")

# 13️⃣ Visualizar el aprendizaje
plt.plot(history.history['loss'], label='Pérdida de entrenamiento')
plt.plot(history.history['val_loss'], label='Pérdida de validación')
plt.xlabel('Épocas')
plt.ylabel('Error cuadrático medio')
plt.title('Evolución del entrenamiento')
plt.legend()
plt.show()

# 14️⃣ Hacer una predicción con nuevos datos (ejemplo)
nueva_muestra = np.array([[2, 350, 4.5]])  # cantidad, precio unitario, rating
nueva_muestra_scaled = scaler.transform(nueva_muestra)
prediccion = model.predict(nueva_muestra_scaled)
print(f"\nPredicción de ventas esperadas (INR): {prediccion[0][0]:.2f}")

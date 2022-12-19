#==========================Importacion==============================
!pip install geopandas
import pandas as pd
import geopandas as gpd
import datetime
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px 
import seaborn as sns
import math
import os
import zipfile

#==========================Lectura==============================
# descomprime el dataset en archivos csv
with zipfile.ZipFile('Covid-19.zip', 'r') as zip_ref:
    zip_ref.extractall('/content/Covid_19')
    zip_ref.close()

# muestra los csv de los que disponemos
for dirname, _, filenames in os.walk('/content/Covid_19'):
    for filename in filenames:
        print(os.path.join(dirname, filename))

#==========================Primer analisis==============================        
worldometer = pd.read_csv("/content/Covid_19/worldometer_data.csv")
worldometer.head()

#==========================Cambios==============================
# Renombrar columnas
worldometer.rename(columns = {'Country/Region':'Country', 'Serious,Critical': 'Critical'}, inplace = True)

# Probar que hay valores nulos en el dataset
print(f"Hay valores nulos en el dataset: {worldometer.isnull().values.any()}")

# Reemplazar valores NaN por 0 en los campos numericos
numerical = worldometer.select_dtypes(include=['float64', 'int64']).columns
worldometer[numerical] = worldometer[numerical].fillna(0)

# Escribir los numeros de la población como millon de unidad
worldometer["Population"] = worldometer["Population"].apply(lambda x: x/1000000)

print(f"La tabla tiene {worldometer.shape[0]} filas y {worldometer.shape[1]} columnas")


#==========================grafico==============================

# Veamos que continentes tiene mas datos registrados sobre covid-19
counts = worldometer.Continent.value_counts()

# Configuraciones
plt.figure(figsize=(10,6))
plt.title("Cantidad de registros por continente")
plt.ylabel("Paises Registrados")
colors = sns.color_palette('pastel')[0:6]

# Crea el bar char
sns.barplot(x=counts.index, y=counts.values, palette=colors)

#==========================Indice==============================

countries = worldometer.Country

# Probamos que no tiene valores nulos
print("No tiene valores nulos" if len(countries[countries.isnull()].head()) == 0 else "Tiene valores nulos")

# Chequeamos que la longitud del Series resultante sea la misma que la cantidad de paises unicos
len(countries[~(countries.duplicated(keep = 'last'))]), len(countries.unique())

# Podemos setear a la Columna Country como el indice del dataset
worldometer.set_index('Country', inplace=True)
worldometer.head()

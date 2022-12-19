#==========================muertes por contiente==============================

# Se muestra las muertes de personas por COVID según continente
muertes = worldometer.groupby("Continent")["TotalDeaths"].sum()

# Configuraciones
plt.title("Porcentaje de muertes totales por continente")
colors = sns.color_palette('pastel')[0:6]

# genera un donut chart
plt.pie(muertes, labels = muertes.index, colors = colors, autopct='%.0f%%', shadow=True)
centre_circle = plt.Circle((0,0),0.7,color='black', fc='white',linewidth=1.25)
fig = plt.gcf()
fig.gca().add_artist(centre_circle)
plt.axis('equal')

plt.show()

#==========================muertes por poblacion==============================

# Toma la suma total de habitantes y muertes por contienetes y los une en un dataframe
muertes = worldometer.groupby("Continent")["TotalDeaths"].sum()
habitantes = worldometer.groupby("Continent")["Population"].sum()
muerte_habitantes = pd.merge(muertes, habitantes, right_index = True, left_index = True)

# Bubble scatter plot
fig = px.scatter(muerte_habitantes, x=muerte_habitantes.index, y="TotalDeaths",
                 size="Population", color="TotalDeaths", size_max=200)

fig.show()

#==========================muertes por vacunas==============================

# Cargamos en memoria el dataframe con datos sobre vacunaciones en el mundo y exploramos los datos
vaccinations = pd.read_csv("Covid_19/vaccinations.csv")
vaccinations.tail()

print(f"El dataset  tiene {vaccinations.shape[0]} filas y {vaccinations.shape[1]} columnas")

# Notar que el dataset posee muchos valores nulos en varias columnas
missing_val_count_by_colomns = vaccinations.isnull().sum()
print(missing_val_count_by_colomns[missing_val_count_by_colomns>0])

# Tomar el máximo de vacunas aplicadas por países
vacc_no_nan = vaccinations[vaccinations["total_vaccinations"].notna()]
vacc_no_nan["date"] = pd.to_datetime(vacc_no_nan["date"])
vacc_no_nan[(vacc_no_nan["date"] >= pd.Timestamp("2020-01-01")) & (vacc_no_nan["date"] < pd.Timestamp("2021-01-01"))]

# Tomar el máximo de muertes por países
maximos_vac = vacc_no_nan.groupby("location")["total_vaccinations"].max().reset_index().set_index("location")
world_no_nan = worldometer[worldometer["TotalDeaths"].notna()]

# Reemplazar TotalDeaths NaN por el promedio
world_no_nan = worldometer[worldometer["TotalDeaths"].notna()]
world_promedio = world_no_nan["TotalDeaths"].mean()
world_death = worldometer.copy()
world_death["TotalDeaths"] = world_death["TotalDeaths"].fillna(world_promedio)

# Se unen los datos de las vacunaciones con el de los casos de Covid a nivel mundial
concatenacion = pd.concat([maximos_vac, world_death], join="inner", axis=1)

# Se obtiene la relacion entre la cantidad de muertes y cantidad de vacunas
relacion = (concatenacion["TotalDeaths"] / concatenacion["total_vaccinations"]).reset_index()
relacion = relacion.rename(columns={"index": "Country", 0: "Relacion"}).sort_values(by="Relacion", ascending=False).head(20);

# Grafico de la relacion
px.scatter(relacion, x="Country", y="Relacion", 
           size=concatenacion.sort_values(by="TotalDeaths", ascending=False).head(20)["TotalDeaths"],
           title="Países con más muertes según la cantidad de vacunas")

# Grafico experimento sobre la relacion
px.scatter(concatenacion, x=concatenacion.total_vaccinations,
           y=concatenacion.TotalDeaths, color=concatenacion.Continent, 
           text=concatenacion.index,
           size=concatenacion.Population, size_max=100)


#==========================muertes por pib==============================

# Ingresar csv
gdp = pd.read_csv("/content/Covid_19/gpd_by_country.csv")
gdp.head()

# Renombrar columnas
gdp.rename(columns={"Country Name": "Country", "GDP per Capita": "gdp_per_capita"}, inplace=True)

# Cambiar GDP a mil millones como unidad
gdp["GDP"] = gdp["GDP"].apply(lambda x: x/1000000000)

# Nos quedamos solo con datos del 2020
gdp = gdp[gdp["Year"] == 2020]

# Setear los paises como indices
gdp = gdp.set_index("Country")

# Concatena el pib con la cantidad de muertes
union = pd.concat([gdp, world_death, maximos_vac], axis=1, join="inner")

# Genera un scatter plot
px.scatter(union, x = 'gdp_per_capita', y = 'TotalDeaths', color = 'total_vaccinations')

#==========================muertes por confirmados==============================

# Relacion de la cantidad de muertes con la cantidad de casos activos
ContinentActiveDeaths = worldometer.groupby(['Continent'])[['TotalCases','TotalDeaths']].sum()
ContinentActiveDeaths.sort_values(['TotalCases'], ascending=False, inplace=True)

# Genera un bar plot de doble barra
anchos = [0.4] * 6
fig = go.Figure()

# Barras de Casos totales 
fig.add_trace(go.Bar(x = ContinentActiveDeaths.index,
                     y = ContinentActiveDeaths['TotalCases'], 
                     width = anchos, name = 'Casos totales'))

# Barras de muertes totales
fig.add_trace(go.Bar(x = ContinentActiveDeaths.index,
                     y = ContinentActiveDeaths['TotalDeaths'], 
                     width = anchos, name = 'Muertes Totales'))

# Configuraciones
fig.update_layout(title =  "Estadisticas por Continente",
                  barmode = 'group', title_font_size = 40)
fig.update_xaxes(title_text = 'Continente')
fig.update_yaxes(title_text = "Nro. de casos")

fig.show()


#==========================Vista mundial==============================

# Genera un nuevo dataframe
latest_map = worldometer.groupby('Country')['ActiveCases','TotalCases','TotalDeaths'].sum().reset_index()
latest_map = latest_map.sort_values(by=['ActiveCases','TotalCases','TotalDeaths'], ascending = False)

# Genera un mapa mundial coloreado segun la cantidad de muertes de cada pais
fig = px.choropleth(latest_map, locations ='Country', 
                    locationmode = 'country names',color = 'TotalDeaths',
                    range_color = [1,120000], labels={"TotalDeaths": "Muertes"})

# Setea un titulo
fig.update_layout(title ="Record de muertes por pais")

fig.show()


#==========================muertes por confirmados por pais==============================

# Nos enfocamos solo en Norteamerica ya que fue el continente mas afectado
northA = worldometer[worldometer["Continent"] == "North America"]
muertes_por_paises = northA.groupby("Country").sum("TotalDeaths")
casos_por_paises = northA.groupby("Country").sum("TotalCases")

# Solo consideramos 15 paise de NorteAmerica para simplificar el analisis y visualizacion
relacion = (muertes_por_paises["TotalDeaths"] / casos_por_paises["TotalCases"] * 100).reset_index()
relacion = relacion.rename(columns = {0: "Relacion"}).sort_values(by = "Relacion", ascending = False).head(15)
relacion.set_index("Country", inplace=True)

# Configuracion del grafico
plt.figure(figsize=(20,5))
colors = sns.color_palette('pastel')[0:len(relacion)]
plt.xticks(rotation=45)
plt.title("Porcentaje de relacion de casos totales sobre la cantidad de muertes")

plt.bar(list(relacion.index), list(relacion.Relacion), width = 0.5, color=colors)


#==========================Conclusion==============================

""" Concluimos en que no podemos determinar que la cantidad de muertes por Covid-19 dependa directamente de alguna de estas variables,
    sino de una combinacion de ellas y otras de las que no disponemos en los datasets.

    Pero si podemos probar que hubo paises mas efectados que otros, algunos en la fatalidad de las personas,
    otros en la cantidad de contagiados, otros segun la cantidad de vacunas. """

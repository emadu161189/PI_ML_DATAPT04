
PI DATA PT 04 – STEAM RECOMMENDER – EMANUEL DUENK

Descripción:
Este proyecto consiste en la explotación de datos provistos por Steam para generar una aplicación consumible que permita direccionar estrategias de ventas en base a los requerimientos de los usuarios. 
En este trabajo se crea una API utilizando FastAPI que proporciona varias rutas (endpoints) para obtener información relacionada con juegos de Steam y reseñas de usuarios. La API permite a los usuarios realizar consultas y obtener recomendaciones basadas en diferentes criterios.

Endpoints:
1. /PlayTimeGenre/{genero}
•	Descripción: Obtiene el año de lanzamiento con más horas jugadas para un género específico.
2. /UserForGenre/{genero}
•	Descripción: Obtiene el usuario con más horas jugadas en un género específico y los tres años en los que más jugó.
3. /UsersRecommend/{anio}
•	Descripción: Obtiene las tres mejores recomendaciones de juegos para un año específico.
4. /UsersNotRecommend/{anio}
•	Descripción: Obtiene las tres peores recomendaciones de juegos para un año específico.
5. /sentiment_analysis/{anio}
•	Descripción: Obtiene el análisis de sentimiento de las reseñas de juegos para un año específico.
6. /recomendacion_usuario/{id_usuario}
•	Descripción: Obtiene recomendaciones de juegos para un usuario específico basadas en su historial de juegos.

Uso de la API:
Esta API se puede utilizar para obtener información detallada sobre los juegos de Steam, las reseñas de los usuarios y las recomendaciones de juegos basadas en diferentes criterios. Se puede acceder a los endpoints mediante solicitudes HTTP GET y recibir respuestas en formato JSON.

Requisitos:
El código utiliza las bibliotecas pandas, fastapi, random, cosine_similarity y uvicorn. Asegúrate de tener estas bibliotecas instaladas antes de ejecutar el código.

Datasets:
Transformando los datasets proporcionados se obtienen los archivos Parquet necesarios (timeforgenre, userforgenre, recommend, sentiment_analysis, users_items, items_recomendacion), estos deben estar en el mismo directorio que el código main.

Extraccion, transformacion y carga de datos(ETL):

Creación de Dataframes a partir de Archivos JSON:
El código comienza creando dataframes a partir de tres archivos JSON, cada uno relacionado con juegos de Steam, reseñas de usuarios y datos de usuario.
Dado algunos errores con el formato de los archivos JSON brindados (comillas simples en lugar de comillas dobles) se crea la siguiente función para la obtención de los DF:
•	crear_dataframe_json_error(path): Esta función se encarga de corregir errores en el formato de archivos JSON donde las claves de los diccionarios utilizan comillas simples en lugar de comillas dobles. Toma la ruta del archivo JSON comprimido como argumento, lo descomprime, divide el contenido en líneas y crea un DataFrame de Pandas.

Limpieza de Datos:
Se realizan varias tareas de limpieza de datos, que incluyen:
•	Eliminación de filas duplicadas en función del campo 'id'.
•	Desanidado de listas con codificación binaria.
•	Extracción de año en datos fechas.
•	Reemplazo de valores nulos de precios por ceros en caso de indicios de contenido gratuito.
•	Reemplazo de valores nulos por la media en el campo 'price'.
•	Reemplazo de datos nulos de variables categóricas por la leyenda 'Dato Desconocido'.
•	Conversión de todos los datos de texto a minúsculas para facilitar la lectura de los endpoints.

Análisis de Sentimientos:
Se realiza un análisis de sentimientos en las reseñas de los usuarios para determinar si son positivas, negativas o neutrales utilizando Textblob

Creación de Dataframes para Consultas y Análisis:
Con el objetivo de optimizar recursos dadas las limitaciones de la cuenta gratuita de Render, se crean varios dataframes que se utilizan para consultas y análisis específicos. 
Estos incluyen:
•	Dataframe para analizar las horas jugadas por año de lanzamiento y género de los juegos (endpoint 1).
•	Dataframe para identificar el usuario con más horas jugadas en un género específico y los años en que más jugó (endpoint 2).
•	Dataframes para analizar las recomendaciones de juegos y puntuaciones de sentimiento (endpoints 3 y 4).
•	Dataframe para analizar los sentimientos positivos, neutrales y negativos en reseñas de juegos por año de lanzamiento (endpoint 5).

Sistema de Recomendación de Juegos en base a usuario:
El código también crea un sistema de recomendación de juegos que utiliza un puntaje de recomendación calculado en función de las reseñas de los usuarios. Los juegos recomendados se basan en la similitud de género, etiquetas, especificaciones y desarrolladores.

Uso de los Dataframes:
Los dataframes resultantes se guardan en archivos Parquet, lo que facilita su acceso y consulta en futuras aplicaciones o análisis de datos

Requisitos:
El código utiliza bibliotecas de Python, como pandas, gzip, re, textblob y sklearn. Asegúrate de tener estas bibliotecas instaladas antes de ejecutar el código.

Análisis Exploratorio de Datos (EDA) con Pandas y Visualización:
Se utiliza Pandas y visualizaciones con Matplotlib y Seaborn. El análisis se realiza sobre los tres conjuntos de datos brindados por la plataforma Steam: steam_games, user_reviews y users_items. 

Funciones creadas:
•	imprimir_ejemplos(df, variables): Muestra un ejemplo no nulo de cada variable del DataFrame.
•	repres_categoricas(df, columna): Realiza un análisis de variables categóricas, incluyendo la creación de una nube de palabras y la identificación de las palabras más frecuentes en una columna categórica.
•	diagrama_caja(df, campo): Crea un diagrama de caja para un campo específico en un DataFrame.
•	dispersion(df, campo_x, campo_y): Crea un gráfico de dispersión entre dos campos en un DataFrame.
•	histograma(df, campo): Crea un histograma para un campo específico en un DataFrame, incluyendo la eliminación de valores atípicos.

Visualizaciones Realizadas:
•	Se cargan los tres conjuntos de de Steam: steam_games, user_reviews y users_items. Se realiza un análisis inicial de cada conjunto de datos, incluyendo la visualización de las primeras filas y la obtención de información básica.
•	Se clasifican las variables en las categorías de variables categóricas y numéricas.
•	Se muestran ejemplos no nulos de variables numéricas y categóricas en el conjunto de datos steam_games.
•	Se realizan análisis univariados de variables categóricas, incluyendo la creación de nubes de palabras y la identificación de las palabras más frecuentes en columnas como 'publisher', 'app_name', 'tags' y 'specs'. 
•	Se realiza un análisis multivariado en el conjunto de datos steam_games mediante una matriz de correlación de las variables numéricas.
•	Se muestra información y ejemplos de variables en los conjuntos de datos user_reviews y users_items.

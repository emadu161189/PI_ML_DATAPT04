import pandas as pd
import gzip as gz
import re
from textblob import TextBlob
from sklearn.preprocessing import LabelEncoder

#DECLARACION DE FUNCIONES

#Debido a que 2 de los 3 archivos json tienen un error (las claves de los diccionarios usan comilla simple,
#cuando la sintaxis de json requiere que sean comillas dobles) se crea la funcion crear_dataframe_jason_error la cual toma por argumento
#la ruta para acceder al archivo json comprimido, descomprime el mismo como texto, separa las lineas creando una lista de lineas,
#itera por cada una de ellas convirtiendolas en diccionarios mediante la funcion eval y guardando cada uno de ellos en una lista
#de diccionarios, luego se crea un dataframe con pandas a partir de dicha lista de diccionarios el cual retorna la funcion.
def crear_dataframe_json_error(path):
    with gz.open(path, 'rt', encoding='utf-8') as archivo:
        dataset = archivo.read()

    lineas = dataset.strip().split('\n')
    lista_de_diccionarios = []
    for linea in lineas:
        diccionario = eval(linea)
        lista_de_diccionarios.append(diccionario)
    
    df = pd.DataFrame(lista_de_diccionarios)

    return df

#Funcion codificacion binaria
def codificacion_binaria_genero(df, columna):

    # Expandir las listas en nuevas columnas binarias
    datos_expandidos = pd.get_dummies(df[columna].apply(pd.Series).stack())
    datos_expandidos = datos_expandidos.groupby(level=0).sum()
    # Combinar el DataFrame original con las nuevas columnas binarias
    df = pd.concat([df, datos_expandidos], axis=1)
    # Eliminar la columna 'caracteristicas' original si es necesario
    df.drop(columna, axis=1, inplace=True)
    
    return df

#Funcion codificacion binaria
def codificacion_binaria_universal(df, columna):

    # Expandir las listas en nuevas columnas binarias
    stack = df[columna].apply(pd.Series).stack().head(100)
    datos_expandidos = pd.get_dummies(stack)
    datos_expandidos = datos_expandidos.groupby(level=0).sum()
    # Combinar el DataFrame original con las nuevas columnas binarias
    df = pd.concat([df, datos_expandidos], axis=1)
    # Eliminar la columna 'caracteristicas' original si es necesario
    df.drop(columna, axis=1, inplace=True)
    
    return df

#Funcion asignar valor a valores nulos y str de la variable precio
def asignar_precio(dato):
    global free
    if type(dato) == str:
        dato = dato.lower()

        if 'free' in dato:
            free.append(True)
            return float(0)#Si el dato contiene la palabra free se le asigna un precio $0
        
        elif 'starting' in dato:
            precio = '0'
            precio = re.findall(r'\$(\S+)', dato)
            precio = ''.join(precio)
            precio = float(precio)#Si el dato contiene la palabra starting y un valor numerico devuelve dicho valor, en el caso que no haya valor numerico devolvera 0
            free.append(False)
            return precio
        else:
            free.append(False)
            return float(0)
    else:
        free.append(False)        
        return dato

#Funcion extraer año de un string
def extraer_anio(dato):
    anio = '1900'
    if type(dato) == str:
        anio = re.findall(r'\d{4}', dato)
        anio= ''.join(anio)       
        return anio
    return dato

#Funcion quitar caracteres extraños
def limpiar(dato):
    if type(dato) == list:
        dato = '-'.join(dato)
        reemplazos = ["{", "}", "'", '[', ']', ':', ',', '"', ';', '/']
        for elemento in reemplazos:
            dato = dato.replace(elemento, "")
        dato = dato.strip()
        return dato
    elif type(dato) == str:
        dato = ''.join(dato)
        reemplazos = ["{", "}", "'", "", '[', ']', ':', ',', '"', ';', '/']
        for elemento in reemplazos:
            dato = dato.replace(elemento, "")
        dato = dato.strip()
        return dato
    else:
        return dato

#Funcion analisis de sentimiento
def analisis_sentimiento(dato):
    analisis = TextBlob(dato)
    polaridad = analisis.sentiment.polarity
    if polaridad > 0:
        return 2
    elif polaridad < 0:
        return 0
    else:
        return 1
    
#Funcion para transformar todos los datos str a minuscula (facilita lectura endpoints)
def str_minuscula(dato):
    if type(dato) == str:
        dato = dato.lower()
    return dato


#Se crea el dataframe df_steam_games con pandas accediendo directamente al archivo json ya que el mismo esta correcto
steam_games = pd.read_json("C:/Users/eduen/AppData/Local/Temp/steam_games.json.gz", lines=True, compression='gzip')

#Se crea el dataframe df_user_reviews a partir del archivo json utilizando la funcion crear_dataframe_json_error
user_reviews = crear_dataframe_json_error("C:/Users/eduen/AppData/Local/Temp/user_reviews.json.gz")

#Se crea el dataframe df_users_items a partir del archivo json utilizando la funcion crear_dataframe_json_error
users_items = crear_dataframe_json_error("C:/Users/eduen/AppData/Local/Temp/users_items.json.gz")



df_steam_games = steam_games.copy()
#Eliminar filas repetidas en funcion del campo 'id'
df_steam_games = df_steam_games.dropna(subset=['id'])
df_steam_games = df_steam_games.drop_duplicates(subset=['id'])
df_steam_games.loc[:, 'item_id'] = df_steam_games['id']
#Desanidar genres realizando codificacion binaria
df_genres = codificacion_binaria_genero(df_steam_games[['item_id','genres']], 'genres')
df_steam_games = pd.merge(df_steam_games, df_genres, on='item_id', how='outer')
#Desanidar tags, specs y developer realizando codificacion binaria limitada hasta 100 elementos por fila
df_tags = codificacion_binaria_universal(df_steam_games[['item_id','tags']], 'tags')
df_specs = codificacion_binaria_universal(df_steam_games[['item_id','specs']], 'specs')
df_developer = codificacion_binaria_universal(df_steam_games[['item_id','developer']], 'developer')
df_steam_games = df_steam_games.drop(columns= ['genres', 'id'])
df_steam_games = df_steam_games.drop_duplicates(subset='item_id')
#Convertir 'item_id' de genres a entero
df_genres['item_id'] = df_genres['item_id'].astype(int)
#Eliminar filas que no contengan valor en 'title'
df_steam_games = df_steam_games.dropna(subset=['title'])
#Reemplazar los valores tipo str por numericos en el campo 'price'
free = []
df_steam_games['price'] = df_steam_games['price'].apply(asignar_precio)
#Reemplazar valores nulos por la media en 'price'
df_steam_games['price'] = df_steam_games['price'].fillna(df_steam_games['price'].mean())
#Extraer año de fechas
df_steam_games['release_date'] = df_steam_games['release_date'].apply(extraer_anio)
#Campo 'release_date' a formato fecha
df_steam_games['release_date'] = pd.to_datetime(df_steam_games['release_date'], format= '%Y', errors= 'coerce').dt.year
df_steam_games['release_date'] = df_steam_games['release_date'].astype(str)
df_steam_games['release_date'] = df_steam_games['release_date'].apply(lambda x: x[:4])
df_steam_games['release_date'] = pd.to_numeric(df_steam_games['release_date'], errors='coerce')
df_steam_games = df_steam_games.dropna(subset='release_date')
df_steam_games['release_date'] = df_steam_games['release_date'].astype(int)
#Reemplazar datos nulos de variables categoricas por la leyenda 'Dato Desconocido'
lista_columnas = ['publisher', 'title', 'url', 'tags', 'specs', 'developer']
for elemento in lista_columnas:
    df_steam_games[elemento].fillna('Dato Desconocido', inplace= True)
    df_steam_games[elemento] = df_steam_games[elemento].astype(str)
#Convertir 'item_id' a entero
df_steam_games['item_id'] = df_steam_games['item_id'].astype(int)
df_steam_games = df_steam_games.drop_duplicates()
df_steam_games = df_steam_games.map(str_minuscula)
df_steam_games = df_steam_games.map(limpiar)

df_steam_games.to_parquet('steam_games', index= False)

#Dataset user_reviews
df_user_reviews = user_reviews.copy()
df_lista = []
for indice, linea in df_user_reviews.iterrows():
    df = pd.DataFrame(linea['reviews'])
    df['user_id'] = linea['user_id']
    df_lista.append(df)

df_user_reviews = pd.concat(df_lista, ignore_index=True)
#Feature engineering
df_user_reviews['sentiment_analysis'] = df_user_reviews['review'].apply(analisis_sentimiento)
#Eliminar la columna last_edited por poseer faltantes
df_user_reviews = df_user_reviews.drop(columns=['last_edited', 'helpful', 'funny'])
df_user_reviews = df_user_reviews.drop_duplicates()
df_user_reviews['posted'] = df_user_reviews['posted'].apply(extraer_anio)
df_user_reviews['posted'] = df_user_reviews['posted'].astype(str)
df_user_reviews['posted'] = df_user_reviews['posted'].apply(lambda x: x[:4])
df_user_reviews['posted'] = pd.to_numeric(df_user_reviews['posted'], errors='coerce')
df_user_reviews = df_user_reviews.dropna(subset='posted')
df_user_reviews['posted'] = df_user_reviews['posted'].astype(int)
df_user_reviews = df_user_reviews.map(limpiar)
df_user_reviews = df_user_reviews.map(str_minuscula)
df_user_reviews['item_id'] = df_user_reviews['item_id'].astype(int)

df_user_reviews.to_parquet('user_reviews', index= False)

df_users_items = users_items.copy()
df_lista = []
for indice, linea in df_users_items.iterrows():
    df = pd.DataFrame(linea['items'])
    df['user_id'] = linea['user_id']
    df['items_count'] = linea['items_count']
    df['steam_id'] = linea['steam_id']
    df['user_url'] = linea['user_url']
    df_lista.append(df)

df_users_items = pd.concat(df_lista, ignore_index=True)
df_users_items = df_users_items.drop(columns= ['item_name', 'steam_id']) #User id y Steam id poseen datos identicos.
df_users_items = df_users_items.drop_duplicates()
df_users_items = df_users_items.dropna()
df_users_items = df_users_items.map(limpiar)
df_users_items = df_users_items.map(str_minuscula)
df_users_items['user_id'] = df_users_items['user_id'].astype(str)
df_users_items['item_id'] = df_users_items['item_id'].astype(int)
df_users_items['playtime_forever'] = df_users_items['playtime_forever'].astype(int)

df_users_items.to_parquet('users_items', index= False)
#Crear dataframe genero relacionado con items, fecha de lanzamiento y usuarios.
genero = pd.merge(df_steam_games[['item_id', 'release_date']], df_genres, on='item_id', how='outer')
genero = pd.merge(genero, df_users_items[['item_id', 'playtime_forever', 'user_id']], on='item_id', how='outer')
genero = genero.drop_duplicates(subset='item_id')
genero['playtime_forever'] = genero['playtime_forever'].fillna(0)
genero['playtime_forever'] = genero['playtime_forever'].astype(int)
genero['release_date'] = genero['release_date'].fillna(0)
genero['release_date'] = genero['release_date'].astype(int)
genero['item_id'] = genero['item_id'].astype(int)

#DF para endpoint 1
timeforgenre = genero.copy()
lista_df = []
for x in timeforgenre.columns:
    if x != 'item_id' and x != 'release_date' and x != 'playtime_forever' and x != 'user_id':
        df = timeforgenre[timeforgenre[x] == 1]
        df = df.groupby('release_date')['playtime_forever'].sum().reset_index()
        df['genero'] = x
        lista_df.append(df)
    else:
        continue
timeforgenre = pd.concat(lista_df, ignore_index=True)
timeforgenre = timeforgenre.drop_duplicates()

timeforgenre.to_parquet('timeforgenre', index= False)

#DF para endpoint 2
userforgenre = genero.copy()
lista_df = []
for x in userforgenre.columns:
    if x != 'item_id' and x != 'release_date' and x != 'playtime_forever' and x != 'user_id':
        df = userforgenre[userforgenre[x] == 1]
        df = df.groupby(['user_id', 'release_date'])['playtime_forever'].sum().reset_index()
        df['genero'] = x
        lista_df.append(df)
    else:
        continue
userforgenre = pd.concat(lista_df, ignore_index=True)
userforgenre = userforgenre.drop_duplicates()

userforgenre.to_parquet('userforgenre', index= False)

#DF para endpoint 3 y 4
recommend = pd.merge(df_steam_games[['item_id', 'title']], df_user_reviews[['item_id', 'posted', 'recommend', 'sentiment_analysis']], on='item_id', how='outer')
recommend = recommend.groupby(['item_id', 'title', 'posted'])[['recommend', 'sentiment_analysis']].mean().reset_index()
recommend['puntaje_recomendacion'] = recommend['recommend'] + recommend['sentiment_analysis']
recommend = recommend.drop(columns= ['recommend', 'sentiment_analysis'])
recommend = recommend.drop_duplicates()
recommend['item_id'] = recommend['item_id'].astype(int)

recommend.to_parquet('recommend', index= False)

sentiment_analysis = pd.merge(df_steam_games[['item_id', 'release_date']], df_user_reviews[['item_id', 'sentiment_analysis']], on='item_id', how='outer')
sentiment_analysis = sentiment_analysis.dropna(subset='release_date')
sentiment_analysis['positivo'] = sentiment_analysis['sentiment_analysis'].apply(lambda x: True if x == 2 else False)
sentiment_analysis['neutral'] = sentiment_analysis['sentiment_analysis'].apply(lambda x: True if x == 1 else False)
sentiment_analysis['negativo'] = sentiment_analysis['sentiment_analysis'].apply(lambda x: True if x == 0 else False)
sentiment_analysis = sentiment_analysis.groupby('release_date')[['positivo', 'neutral', 'negativo']].sum().reset_index()

sentiment_analysis.to_parquet('sentiment_analysis', index= False)

#Sistema de recomendacion
puntaje_recomendacion = recommend.copy()
puntaje_recomendacion = puntaje_recomendacion.groupby('item_id')['puntaje_recomendacion'].mean().reset_index()

items_recomendacion = pd.merge(df_steam_games, puntaje_recomendacion, on='item_id', how='outer' )
items_recomendacion = pd.merge(items_recomendacion, df_tags, on='item_id', how='outer' )
items_recomendacion = pd.merge(items_recomendacion, df_specs, on='item_id', how='outer' )
items_recomendacion = pd.merge(items_recomendacion, df_developer, on='item_id', how='outer' )
items_recomendacion = items_recomendacion.drop_duplicates(subset='item_id')
items_recomendacion = items_recomendacion.dropna(subset='title')
label_encoder = LabelEncoder()
for col in items_recomendacion.columns:
    if col != 'item_id' and col != 'title' and col != 'puntaje_recomendacion':
        items_recomendacion[col] = label_encoder.fit_transform(items_recomendacion[col])
items_recomendacion = items_recomendacion.fillna(0)
items_recomendacion['item_id'] = items_recomendacion['item_id'].astype(int)

items_recomendacion.to_parquet('items_recomendacion', index= False)
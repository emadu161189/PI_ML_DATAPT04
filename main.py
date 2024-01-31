import pandas as pd
import random
from sklearn.metrics.pairwise import cosine_similarity
import uvicorn
from fastapi import FastAPI

app = FastAPI()

@app.get("/PlayTimeGenre/{genero}")
def PlayTimeGenre(genero: str):
    genero = genero.title()
    filtro = [('genero', "==", genero)]
    try:
        df = pd.read_parquet('timeforgenre', filters=filtro )
        max = df[df['playtime_forever'] == df['playtime_forever'].max()]
        
        return {f"Año de lanzamiento con más horas jugadas para Género {genero}" : str(max['release_date'].iloc[0])}
  
    except Exception as e:
        error_message = str(e)
        return f'Error: {error_message}'

@app.get("/UserForGenre/{genero}")
def UserForGenre(genero: str):
    genero = genero.title()
    filtro = [('genero', "==", genero)]
    try:
        df = pd.read_parquet('userforgenre', filters=filtro )
        #usuario con mas horas jugadas en el genero
        df_max = df.groupby('user_id')['playtime_forever'].sum().reset_index()
        df_max = df_max[df_max['playtime_forever'] == df_max['playtime_forever'].max()]
        #Top 3 años con mas horas jugadas
        df_top = df[df['user_id'] == df_max['user_id'].iloc[0]]
        df_top = df_top.nlargest(3, 'playtime_forever')

        return {f"Usuario con más horas jugadas para Género {genero}" : str(df_max['user_id'].iloc[0]), 
                "Horas jugadas":[{"Año": str(df_top['release_date'].iloc[0]), "Horas": str(df_top['playtime_forever'].iloc[0])},
                {"Año": str(df_top['release_date'].iloc[1]), "Horas": str(df_top['playtime_forever'].iloc[1])}, 
                {"Año": str(df_top['release_date'].iloc[2]), "Horas": str(df_top['playtime_forever'].iloc[2])}]}
        
    except Exception as e:
        error_message = str(e)
        return f'Error: {error_message}'


@app.get("/UsersRecommend/{anio}")
def UsersRecommend(anio: int):
    filtro = [('posted', "==", anio)]
    try:
        df = pd.read_parquet('recommend', columns=['title', 'posted', 'puntaje_recomendacion'], filters=filtro)
        df = df.nlargest(3, ['puntaje_recomendacion'])

        return [{"Puesto 1" : df['title'].iloc[0]}, {"Puesto 2" : df['title'].iloc[1]},{"Puesto 3" : df['title'].iloc[2]}]
    
    except Exception as e:
        error_message = str(e)
        return f'Error: {error_message}'

@app.get("/UsersNotRecommend/{anio}")
def UsersNotRecommend(anio: int):
    filtro = [('posted', "==", anio)]
    try:
        df = pd.read_parquet('recommend', columns=['title', 'posted', 'puntaje_recomendacion'], filters=filtro)
        df = df.nsmallest(3, ['puntaje_recomendacion'])

        return [{"Puesto 1" : df['title'].iloc[0]}, {"Puesto 2" : df['title'].iloc[1]},{"Puesto 3" : df['title'].iloc[2]}]
    
    except Exception as e:
        error_message = str(e)
        return f'Error: {error_message}'

@app.get("/sentiment_analysis/{anio}")
def sentiment_analysis(anio: int):
    filtro = [('release_date', "==", anio)]
    try:
        df = pd.read_parquet('sentiment_analysis', filters=filtro)
        positivo = df['positivo'].iloc[0].astype(str)
        neutral = df['neutral'].iloc[0].astype(str)
        negativo = df['negativo'].iloc[0].astype(str)
        return {"Negativo": negativo, "Neutral": neutral, "Positivo": positivo}
    
    except Exception as e:
        error_message = str(e)
        return f'Error: {error_message}'


@app.get("/recomendacion_usuario/{id_usuario}")
def recomendacion_usuario(id_usuario= str):

    try:
        filtro_in = [('user_id', '==', id_usuario)]
        df_juegos_usuario = pd.read_parquet('users_items', columns=['item_id', 'user_id'], filters=filtro_in)
        flag = True
        while flag:
            item_id = df_juegos_usuario['item_id'].iloc[random.randint(0, len(df_juegos_usuario['item_id']))]
            if item_id:
                flag = False
        filtro_id = [('item_id', '==', item_id)]
        puntaje_recomendacion = pd.read_parquet('items_recomendacion', columns=['puntaje_recomendacion'])
        filtro_mtz = [('puntaje_recomendacion', '>', puntaje_recomendacion['puntaje_recomendacion'].mean())]
        entrada = pd.read_parquet('items_recomendacion', filters=filtro_id)
        if entrada.empty:
            return 'Intente nuevamente'
        datos_entrada = entrada[['item_id', 'title']]
        matriz_entrada = entrada.drop(columns=['item_id', 'title'])
        matriz = pd.read_parquet('items_recomendacion', filters=filtro_mtz)
        datos_matriz = matriz[['item_id', 'title']]
        matriz = matriz.drop(columns=['item_id', 'title'])
        matriz = matriz.fillna(0)
        similitud_coseno = cosine_similarity(matriz_entrada, matriz)
        similitud_serie = pd.Series(similitud_coseno[0], index=matriz.index)
        resultado = matriz.loc[similitud_serie.nlargest(6).index]
        indices = resultado.index
      
        items = []
        for elemento in indices:
            titulo = datos_matriz.loc[elemento]
            if titulo['item_id'].item() == datos_entrada['item_id'].item():
                continue
            items.append(titulo['title'])

        return {f"Juegos recomendados para {id_usuario}": [items[0], items[1], items[2], items[3], items[4]]}
    
    except Exception as e:
        error_message = str(e)
        return f'Error: {error_message}'
 




if __name__ == "__main__":
        uvicorn.run(app)
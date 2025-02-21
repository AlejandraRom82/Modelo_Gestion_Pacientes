"""
API biblioteca Modelo de Gestión de Citas
La funcion load_pacientes() biblioteca carga de pacientes
La funcion get_pacientes() muestra los pacientes cuando alguien lo pida
La funcion get_pacientes(id) muestra los pacientes por numero de
La funcion chatbot(query) es un asistente que busca pacientes segun palabras claves
La funcion get_pacientes_by_category(category) muestra los pacientes por categoria
"""

#Importamos las herramientas necesarias para construir nuestra API
from fastapi import FastAPI, HTTPException #FastAPI nos ayuda a crear la aPI y HTTPException maneja errores.
from fastapi.responses import HTMLResponse, JSONResponse #HTMLResponse para paginas web JSONResponse para respuestas en formato JSON
import pandas as pd # Pandas nos ayuda a manejar datos en tablas como si fuera un excel
import nltk # Es una libreria para procesar texto y analizar palabras
from nltk.tokenize import word_tokenize #Tokenizador se usa para dividir un texto en palabras individuales
from nltk.corpus import wordnet # Nos ayuda a encontrar sinonimos de palabras

#Indicamos la ruta donde NTLT buscara los datos descargados en nuestro computador
nltk.data.path.append('C:\\Users\\USUARIO\\AppData\\Local\\Programs\\Python\\Python312\\Lib\\site-packages\\nltk_data')

#Descargamos las herramientas necesarias de NLTK para el analisis de palabras

nltk.download('punkt') #Paquete para dividir frases en palabras
nltk.download('wordnet') #Paquete para encontrar sinonimos de palabras en ingles
nltk.download('punkt_tab')

# Funcion para cargar pacientes desde un archivo CSV

def load_pacientes():
    #Leemos el archivo que contiene informacion pacientes y seleccionamos la columnas mas importantes
    df = pd.read_csv("dataset/base_datos.csv")[['id','nombre','direccion','ciudad','celular','mail','edad','sintomas','categoria']]
   
    #renombramos las columnas para que sean mas faciles de entender
    df.columns = ['id','nombre','direccion','ciudad','celular','mail','edad','sintomas','categoria']
   
    #Llenamos los espacios vacios con texto vacio y convertimos los datos en una lista de diccionarios
    return df.fillna('').to_dict(orient='records')

#cargamos los pacientes al iniciar la API para no leer el archivo cada vez que alguien pregunte por ellas
pacientes_list = load_pacientes()

#Funcion para encontrar sinonimos de una palabra

def get_synonyms(word):
    #Usamos wordnet para obtener distintas palabras que significan lo mismo
    return {lemma.name().lower() for syn in wordnet.synsets(word) for lemma in syn.lemmas()}

#Creamos la aplicacion FastAPI, que sera el motor de nuestra API
#Esto inicializa la API con un nombre y con una version
app = FastAPI(title="Modelo Inteligente Para La Clasificación De Pacientes Según La Patología", version ="1.0.0")

#Ruta de inicio: Cuando alguien entra a la API sin especificar nada, vera un mensaje de bienvenida

@app.get('/', tags=['Home'])
def home():
    # Cuando entremos en el navegador veremos el mensaje de bienvenida
    return HTMLResponse('<h1>Bienvenido al Modelo Inteligente Para La Clasificación De Pacientes Según La Patología</h1>')

# Obteniendo la lista de los pacientes
# Creamos una ruta para obtener todos los pacientes

# Ruta para obtener todos los pacientes disponibles

@app.get('/pacientes', tags=['Pacientes'])
def get_pacientes():
    # Si hay pacienters, lo enviamos y si no mostramos un error
    return pacientes_list or HTTPException(status_code=500, detail="No hay pacientes disponibles")


# Ruta para obtener un paciente especifica segun su ID
@app.get('/pacientes/Cedula', tags=['pacientes'])
def get_pacientes(id:int):
    #Buscamos en la lista de peliculas la que tenga el mismo ID
    return next((m for m in pacientes_list if m['id'] == id), {"detalle":"Paciente no encontrado"})

#Ruta del chatbot que responde con pacientes segun palabras clave de la categoria

@app.get('/chatbot', tags=['Chatbot'])
def chatbot(query: str):
    # Dividimos la consulta en palabras clave, para entender mejor la intención del usuario
    query_words = word_tokenize(query.lower())
   
    # Buscamos sinonimos de las palabras clave para ampliar la busqueda
    synonyms = {word for q in query_words for word in get_synonyms(q)} | set(query_words)
   
    # Filtramos la lista de pacientes buscando coincidencias en la categoria o en los sintomas
    results = [m for m in pacientes_list if any(s in m['categoria'].lower() for s in synonyms)]
   
    # Si encontramos pacientes, enviamos la lista; si no, mostramos un mensaje de que no se encontraron coincidencias
   
    return JSONResponse(content={
        "respuesta": "Aquí tienes algunos pacientes que coinciden con tu busqueda." if results else "No se encontraron pacientes que coincidan con tu busqueda",
        "pacientes": results
    })

# Ruta para obtener pacientes por categoria especifica

@app.get('/pacientes/by_categoria/Alta-Media-Baja', tags=['Pacientes'])
def get_pacientes_by_categoria(categoria: str):
    # Filtramos la lista de pacientes según la categoría ingresada
    return [m for m in pacientes_list if categoria.lower() in m['categoria'].lower()]

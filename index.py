# Para esta prueba se ha decidido usar la pagina de falabella.
# Para la extracción masiva de la información se ha decidido usar Selenium el cual normalmente se utiliza para 
# realizar pruebas, sin embargo, es muy popular en el mundo del WebScrapping y nos permite navergar dentro de
# las diversas paginas resultantes de la busqueda "Computadores portatiles".
# En la raiz del proyecto se encuentra el driver requerido por selenium para acceder al navegado este se llama
# chromedriver.exe el cual va variando dependiendo del sistema operativo y la versión del navegador; en este caso, se 
# utilizo el dirver para la version 96.0.4 de Google Chrome.
# Se ha decidido utilizar Pandas para organizar la información en DataFrames que representan tablas y de esta manera
# pasar dichas tablas a un documento con extencion csv separado por comas.
# La libreria time nos permite hacer pausas drasticas para que el driver de selenium logre extraer todo el html solicitado,
# de lo contrario no se lograrian extarer todos los productos en su totalidad; ademas, nos ayudamos de la libreria random para
# generar valores aleatorios de tiempo de espera.
from selenium import webdriver
import pandas as pd
import random
import time

# La función extractInfo nos permite extraer la información de los productos y guardarla en documentos los cuales que son
# retornados en una coleccion de documentos y utilizados posteriormente en la funcion main para generar el DataFrame y el 
# archivo csv.
# products representa los productos extraidos por el driver de Selenium los cuales comparten una clase css
# first es representado por un valor booleano y nos indica si es la primera pagina, esto es usado para saber si se deben incluir
# ciertos productos que se repiten en todas las paginas como lo son los productos patrocinados, de esta manera, dichos productos
# aparecen una unica vez en el documento csv. 
def extractInfo(products, first):
    dic_products = [] # Lista de documentos de productos
    for product in products: # Se recorren los productos enviados por el driver
        try:
            # Se busca la etiqueta "patrocinado-title" dentro del producto para saber si es un producto patrocinado,
            # se hace dentro de un try-except porque puede generar excepción al no encontrar la etiqueta 
            sponsor = product.find_element(by = "class name", value = "patrocinado-title").text 
        except:
            sponsor = 'No patrocinado'
        # Si el producto es patrocinado y es la primera pagina o el producto no es patrocinado entonces
        # se extrae la información y se agrega en la lista de documentos, esto se hace para que los productos
        # patrocinados no aparezcan repetidos por cada pagina    
        if((first and sponsor.lower() == 'patrocinado') or (sponsor.lower() != 'patrocinado')):  
            brand = product.find_element(by = 'class name' , value = 'pod-title') # Extaremos la marca por su clase html
            description = product.find_element(by = 'class name' , value = 'pod-subTitle') # Extaremos la descripció por su clase html
            # Extraemos el precio usando su clase html y hacemos un split del valor obtenido para extraer unicamente el numero
            price = product.find_element(by = 'class name' , value = 'price-0').text.split(' ')
            features = product.find_elements(by = 'class name' , value = 'jsx-4018082099')# Extraemos el conjunto de caracteristicas
            # Declaramos las variables que contendran las caracteristicas en None debido a que no todos los productos
            # tienen especificadas todas sus caracteristicas
            processor = None
            ram = None
            screen = None
            hdd = None
            ssd = None
            # Recorremos el conjunto de caracteristicas encontradas
            for feature in features:
                # Por cada caracteristica se extrae el texto y se hace un split usando los : debido a que siempre
                # cada caracteristica tiene su titulo: valor y unicamente queremos el valor
                values = feature.text.split(':')
                if('procesador' in values[0].lower()):# Si el titulo contiene la palabra procesador entonces guarda el valor
                    processor = values[1] 
                elif('ram' in values[0].lower()):# Si el titulo contiene la palabra ram entonces guarda el valor
                    ram = values[1]
                elif('pantalla' in values[0].lower()):# Si el titulo contiene la palabra pantalla entonces guarda el valor
                    screen = values[1]
                elif('hdd' in values[0].lower()):# Si el titulo contiene la palabra hdd entonces guarda el valor
                    hdd = values[1]
                elif('ssd' in values[0].lower()):# Si el titulo contiene la palabra ssd entonces guarda el valor
                    ssd = values[1]
            # Se añade a la lista de productos un nuevo diccionarioque contiene las caracteristicas extraidas anteriormente
            # mediante un if ternario se verifica si se obtuvo resultado de dicha caracteristica, en caso contrario se coloca
            # "NA" indicando que No Aparece 
            dic_products.append({
                "Brand" : brand.text,
                "Description" : description.text,
                "Processor" : "NA" if processor == None else processor,
                "RAM" : "NA" if ram == None else ram,
                "Screen" : "NA" if screen == None else screen,
                "Hard Drive Disc" : "NA" if hdd == None else hdd,
                "State Solid Disc" : "NA" if ssd == None else ssd,
                "Price" : price[1],
            })
    # Se retorna el listado de diccionarios de productos que contiene toda la información de los mismos
    return dic_products
# La funcion findPagesNumber recibe un elemento extraido por el driver de Selenium en donde se contiene el número
# de paginas disponibles para la busqueda de "computadores portatiles"
def findPagesNumber(elements):
    element = elements[len(elements)-1] # Se obtiene el ultimo elemento de la paginación el cual contiene el valor de paginas
    element.find_element(by = 'tag name', value = 'button') # Se obtiene el boton dentro del elemento que contiene el texto
    return element.text # Se retorna el texto de dicho botón


# En la función main se ejecuta toda la logica que invoca las funciones necesarias para completar el proceso
def main():
    # Se guarda en una variable la url a la cual se va a hacer el webscrapping
    url = 'https://www.falabella.com.co/falabella-co/category/cat1361001/Computadores--Portatiles-?sred=computadores-portatiles'
    options = webdriver.ChromeOptions() # Creamos un objeto de tipo opciones para el driver de Chrome
    final_products=[] # Se crea la lista de productos finales
    options.headless = True # Opción de ejecuta el driver en modo headless eso quiere decir que no abre el navegador
    # Evita que el driver ejecute ciertos requerimentos de perifericos como bluetooth y genere errores
    options.add_experimental_option('excludeSwitches', ['enable-logging']) 
    driver = webdriver.Chrome(options=options) # Se crea el driver con las opciones
    driver.get(url) # Se hace la peticion get a la url establecida
    # Con el driver se encuentran los elementos que contienen los valores de paginación y estos son enviados a la 
    # función findPagesNumber
    pages = findPagesNumber(driver.find_elements(by='class name', value='pagination-item'))  
    for page in range(0,int(pages)): # Se hace un ciclo de 0 a la cantidad de paginas con la finalidad de extraer los productos por cada pagina
        try:
            # Con el diver extraemos los elementos de productos por su clase html
            products = driver.find_elements(by = 'class name' , value = 'search-results-list')
            # Enviamos estos elementos a la función extractInfo que nos procesa los elementos y nos devuelve
            # la lista de diccionarios con la información y esta lista se une con la lista ya existente de productos
            final_products += extractInfo(products, True if page == 0 else False) # Mediante un if ternario enviamos True si es la primera pagina o false si no 
            # Buscamos el botón que nos permite ir a la siguiente pagina usando su clase html
            next_button = driver.find_element(by = 'id' , value = 'testId-pagination-bottom-arrow-right')
            next_button.click() # Damos click al botón
            time.sleep(random.uniform(8.0, 10.0)) # Hacemos una espera de un valor aleatorio para dar tiempo a que los elementos html se carguen
        except:
            break
    table = pd.DataFrame(final_products) # Finalmente con los diccionarios armamos un DataFrame de pandas
    table.to_csv('portatiles.csv', index=False, sep=',') # Una vez armado el DataFrame se crea el documeto con extensión csv separado por comas

# Este condicional nos permite hacer la ejecución de la función main
if __name__ == "__main__":
    main()
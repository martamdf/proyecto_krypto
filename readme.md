# SIMULADOR DE COMPRAVENTA DE CRYPTOS ##

## Aplicación web para la simulación de inversiones en criptomonedas. ###

### Instrucciones de instalación:

Estas instrucciones son válidas para realizar la instalación en MacOS. 
A tener en cuenta que debemos de tener instalado SqLite3.

### 1. Clonación del proyecto.

Entrar en el terminal en la ruta donde queramos instalar el proyecto y ejecutar la siguiente sentencia (en este caso nos creará una carpeta de nombre krypto):

` git clone https://github.com/martamdf/proyecto_krypto.git krypto`

### 2. Creación del fichero de la base de datos.

Ir al archivo "initial.py" y ejecutarlo. Creará la base de datos con las tablas necesarias (en kryptoexchange/data/) para que la aplicación funcione correctamente.

### 3. Creación archivo .env.

Crear el archivo .env en nuestra carpeta principal, con las siguientes variables de entorno necesarias:

- FLASK_APP=run.py
- FLASK_ENV=development

### 4. Instalación del Entorno virtual.

En el terminal, estando en nuestra carpeta de proyecto ejecutaremos la siguiente sentencia:

`python3 -m venv venv `

El segundo 'venv', se corresponde con el nombre que hemos dado a nuestro entorno virtual.


### 5. Activación del entorno virtual.

Ejecutar la siguiente instrucción en el terminal:

` source venv/bin/activate `

### 6. Instalación de dependencias.

Instalar las dependencias ejecutando el siguiente mandato: 

` pip install -r requirements.txt `

### 7. Solicitud de API KEY a CoinmarketCap.

Ir a la siguiente URL, y consigue una API KEY:

https://pro.coinmarketcap.com

### 8. Fichero Config.

Realizar una copia del fichero config_template.py y renombrarlo como config.py. 
Establecer una SECRET KEY, introducir la ruta a la base de datos (kryptoexchange/data/exchanges.db), e introducir la API KEY que nos ha proporcionado CoinMarketCap.


Nuestra aplicación estaría lista para funcionar ejecutando el comando "flask run".


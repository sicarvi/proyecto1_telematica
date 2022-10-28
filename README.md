# PIBL

El PIBL (Proxy Inverso + Balanceador de Cargas) permite recibir las peticiones web del cliente, las procesa y las envía a uno de los tres servidores creados detrás de este proxy para finalmente retornar una respuesta.

## Librerías

Se necesita importar los módulos socket, threading y time:
`import socket, threading, time`

```python
import socket, threading, time
```

## ¿Cómo se usa? 
Debemos crear 3 instancias en AWS y en cada una tener un servidor para poder realizar responses.               
Se entra a una consola de comandos y se ejecuta el siguiente comando:
```bash
python pibl.py
```
Si el archivo `serv.config` está correcto el proxy empezará a escuchar peticiones. De lo contrario, en consola aparecerá un mensaje el cual indicará al usuario que el archivo de configuración está incorrecto o no existe.
 
## ¿Por qué python?
- La implementación de la librería de Threading es muy robusta y ofrece un desempeño similar a lenguajes de nivel más bajo lo que lo hace perfecto en términos de entendimiento/eficiencia
- La facilidad de la lectura y compresión de la sintaxis permite a los desarrolladores tener un entorno más ameno a la hora del desarrollo
- Python cuenta con una gran cantidad de métodos para el manejo de su facilidad de procesar almacenar y distribuir strings necesarios para el http
-Por permitir la programación orientada a objetos que se presta para este caso de uso especifico   
## Introducción
El proxy inverso actúa en este caso como un intermediario entre el cliente y los servidores recibiendo un request de parte del cliente, llevando este hasta alguno de los servidores y recibiendo un response de parte de los servidores retornándolo finalmente al cliente. En palabras resumidas el proxy inverso se utiliza como un intermediario para gestionar solicitudes y respuestas. Estos proxies inversos generalmente se utilizan para mejorar el rendimiento y proporcionar un equilibrio de carga para las aplicaciones web, esto lo logra implementando un balanceador de cargas siguiendo el principio de Round Robin, un algoritmo en el que a cada proceso se le asigna un intervalo de tiempo fijo de forma cíclica, esto permite una programación por turnos en donde se asigna una cantidad de tiempo particular a diferentes trabajos.

## Desarrollo
Este proyecto consta de 4 archivos importantes que serían `pibl.py`,`logPIBL.txt`,`serv.config`, `persist.cache`. 

- `pibl.py`: Contiene la clase " " que se encarga de instanciar los métodos y atributos necesarios para que el proxy reciba peticiones de un cliente, para así, enviarlas a uno de los servidores de aplicación determinado por el método Round Robin y finalmente devolver la respectiva respuesta a el cliente original. Esta clase hereda de la implementación de `Thread` de python para que el proxy pueda generar un hilo de procesamiento por cada cliente y así atender solicitudes de manera concurrente.
Además contiene el método `setup` que analiza el archivo de configuración para parametrizar la instancia del proxy.

- `serv.config`: Este es el archivo de configuración de parámetros para el servidor donde recibe un puerto (en el que el proxy escucha las peticiones), proxy (dirección ip del proxy), y servers (string separada por comas de las direcciones ip y los puertos de los servidores donde va a estar alojada la aplicación).  Ejemplo:
```bash
PUERTO=8080
PROXY=127.0.0.1
SERVERS=54.234.27.225:80,34.228.142.29:80,52.201.233.165:80
```

- `logPIBL.txt`: Es el registro de las salidas de consola de forma estructurada. Cuenta con una marca de tiempo (timestamp) que brinda información de cuando se generó, también cuenta con una etiqueta que muestra que evento se procesó. Luego va la ip asociada a ese evento y por último el cuerpo del evento que puede ser una petición o una respuesta del servidor.
    Ejemplo: 
```bash
(16:39:11) [NUEVA CONEXION]: ('127.0.0.1', 62012)
(16:39:11) [NUEVO THREAD]: CL-('127.0.0.1', 62012)
(16:39:11) * REQUEST ('127.0.0.1', 62012)* GET / HTTP/1.1
(16:39:11) [PETICION REALIZADA]: 54.234.27.225
(16:39:17) * RESPONSE ('127.0.0.1', 62012)* HTTP/1.1 200 OK
(16:39:17) * REQUEST ('127.0.0.1', 62012)* GET /icons/ubuntu-logo.png HTTP/1.1
```

- `persist.cache`: Persistencia del cache del servidor proxy donde se almacena cada request/response procesado junto con una marca de tiempo (timestamp) para el posterior cálculo del TTL (Time To Live)

## Conclusiones
- Este proyecto nos ayudó a practicar el lenguaje de programación python. Nos enseño la teoría del HTTP/1.1 y su estructura formal dándonos una idea estructurada de como funciona la librería request, mas específicamente enseñándonos como funcionan los request y los response entre cliente - proxy , servidor proxy. 
- Con este proyecto concluimos que el proxy es un intermediario muy importante en la red ya que mejora enormemente el rendimiento de las solicitudes y con el balanceador de cargas distribuye mejor estas cargas de solicitudes entre los servidores disponibles

## Referencias
Se usó la [Documentación Sockets Python](https://docs.python.org/es/3/howto/sockets.html) para entender como funcionaba el MultiThreading y como funcionaba en sí la librería.   
La [Documentación HTTP/1.1 w3.org](https://www.w3.org/Protocols/HTTP/1.1/draft-ietf-http-v11-spec-01) se usó para conocer a fondo la estructura del HTTP/1.1 y el contenido de sus headers.
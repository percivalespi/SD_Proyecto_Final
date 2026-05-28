# Fases del Desarrollo del Proyecto

~~~
proyecto_distribuidos/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── src/
    ├── IDL.proto
    ├── reloj.py
    ├── servidor_grpc.py
    ├── cliente_grpc.py
    ├── main.py
    └── trigger.py
└── doc/
    ├── notas.md # Documentación de lo que llevo
    ├── requimientos.md # Requisitos que pide el proyecto
    ├── SD_Escenario_PF.drawio # Diagrama de espacio-tiempo del escenario (para modificar con draw.io)
    └── SD_Escenario_PF.png # Diagrama de espacio-tiempo del escenario
~~~

Donde:

- reloj.py: Una clase que maneja la lógica matemática del vector (incrementar, hacer el max, etc.).

- servidor_grpc.py: La clase que define cómo responder a las peticiones (hereda de tu .proto).

- cliente_grpc.py: Una clase con funciones auxiliares para conectarse a otros contenedores.

- main.py: El orquestador. Importa las tres clases anteriores, instancia un solo reloj en memoria, levanta el servidor pasándole ese reloj, y se queda esperando los comandos del trigger.py para usar el cliente.

## ¿Cómo ejecutar el programa?
Aun en desarrollo....

En caso de no tener instalado las dependencias de `grpcio` y `grpcio-tools`, se deben de instalar utilizando el siguiente comando:

Es recomendable crear un entorno virtual para evitar conflictos con otras dependencias de Python en el sistema. 
```bash
python -m venv venv
.venv\bin\activate
```


Instalación de dependencias:
```bash
pip install -r requirements.txt
```

>[!NOTE]
> Para generar las plantillas con grpc ejecutar el siguiente comando en /src:
> 
> `python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. IDL.proto`

### Ejecución con Docker
Para esto es neceario tener clonado el repositorio:
```bash
git clone https://github.com/percivalespi/SD_Proyecto_Final.git
```
Verificar si se cuenta con docker-compose:
```bash
docker-compose --version
```
En caso de no contar con docker-compose se deberá instalar con:
```bash
sudo apt install docker-compose -y
sudo systemctl start docker
sudo systemctl enable docker
docker-compose --version
```
Una vez se tenga el repositorio y docker-compose ahora ejecutar el docker.
```bash
sudo docker-compose build
```
Levantar clúster.
```bash
sudo docker-compose up
```
#### Pruebas de comunicación:

```bash
# Ejecutar evento interno en el proceso 1
sudo docker-compose exec p1 python src/trigger.py interno

# Enviar mensaje de P1 a P5
sudo docker-compose exec p1 python src/trigger.py enviar 5 "Hola desde P1"
```

## Fase 1: Definición y Contratos (COMPLETADA)

- [x] Contrato gRPC: Definir los 4 servicios requeridos (envío, recepción, evento interno y difusión) en src/IDL.proto.  

- [x] Compilación: Ejecutar el comando de grpcio-tools (ahora apuntando a la carpeta src) para generar los archivos _pb2.py y _pb2_grpc.py.

- [x] Diseño del Escenario: Finalizar el diagrama de espacio-tiempo para el escenario de los 5 procesos IoT.  
PDF

## Fase 2: Implementación Modular en Python

- [x] El Estado (src/reloj.py): Programar la clase que mantendrá el vector en memoria y manejará los cálculos lógicos (incrementos y la regla del valor máximo al recibir mensajes).


- [x] El Oyente (src/servidor_grpc.py): Implementar la respuesta a los 4 servicios RPC, actualizando el reloj vectorial de forma correcta e imprimiendo los registros exactos para las bitácoras.  
PDF

- [x] El Hablador (src/cliente_grpc.py): Crear la lógica de conexión para enviar los mensajes hacia otros contenedores, empaquetando el reloj actual del emisor.  
PDF

- [x] El Orquestador (src/main.py): Inicializar la instancia del reloj, arrancar el servidor gRPC y mantener el proceso en un ciclo infinito para que el contenedor no se apague.

- [x] El Disparador (src/trigger.py): Escribir el script CLI que recibirá parámetros por consola y se comunicará con el servidor local para iniciar las acciones.

### Fase 3: Dockerización y Redes

- [x] Empaquetado: Configurar el Dockerfile en la raíz para que instale las dependencias de Python, copie la carpeta src completa al contenedor y ejecute python src/main.py al arrancar.

- [x] Orquestación: Armar el docker-compose.yml para levantar los 5 contenedores de manera simultánea, asegurando que la comunicación sea únicamente interna entre ellos. 

### Fase 4: Pruebas desde Consola y Entregables

- [ ] Ejecución de Pruebas: Poner en práctica tu manejo de la línea de comandos de Linux utilizando docker exec sobre cada contenedor para disparar la secuencia de eventos mediante trigger.py.  

- [ ] Validación: Utilizar comandos de consola para leer las salidas y confirmar que cada evento haya quedado debidamente registrado en su bitácora.  
PDF

- [ ] Demostración: Grabar el video corto donde muestres la terminal ejecutando los contenedores, el envío de mensajes y cómo se actualizan los relojes.  
PDF


# Notas del Desarrollo Propuesto

## Entorno Propuesto
Implementar un sistema distribuido de venta de boletos de cine, donde cada contenedor simula ser un microservicio independiente que se conecta y coordina con diferentes partes del sistema general. 

Los contenedores se encontrarán aislados esperando peticiones o interacciones, sin embargo como son simuladores, al utilizar `docker exec` indicamos que empiecen a generar eventos internos (como la selección de un asiento, verificación de base de datos, etc.).

### Sistema Propuesto

El sistema debe estar compuesto por 5 procesos, simulando una arquitectura orientada a microservicios:

- P1 (App Cliente)
- P2 (Inventario)
- P3 (Notificaciones)
- P4 (Emisión)
- P5 (Orquestador)

### Servicios de gRPC que se deben implementar

En el documento se menciona que se deben de tener 4 servicios de gRPC a implementar

#### 1. Servicio de Envío (Send)
- Parámetros: ID del que envía, ID del que recibe, el mensaje y el reloj vectorial.  
- Comportamiento: Antes de mandar la petición, el proceso emisor debe incrementar su propio reloj vectorial.  
- Registro: Se empaqueta el mensaje con el nuevo reloj vectorial, se envía, y se guarda en la bitácora el evento de envío. 

#### 2. Servicio de Recepción (Receive)
- Parámetros: ID del que envía, el mensaje y el reloj vectorial recibido.  
- Comportamiento: Al recibir la llamada, el proceso actualiza su reloj vectorial local. Esto se hace sacando el valor máximo entre cada posición del reloj local y el reloj recibido.  
- Registro: Se registra el evento de recepción en la bitácora y se devuelve un ACK (acuse de recibo) al emisor para confirmar.

#### 3. Servicio de Evento Interno (Internal)
- Parámetros: No tendrá parámetros.  
- Comportamiento: Simula que el proceso hizo una tarea por su cuenta (interacción del usuario en la app, verificación de base de datos, etc.). Incrementa la posición de su reloj vectorial local.  
- Registro: Se registra en la bitácora el evento interno con el vector actualizado. 

#### 4. Servicio de Difusión (Broadcast)
- Parámetros: Envía un mensaje a todos los procesos del sistema.  
- Comportamiento: El propósito de este cuarto servicio es simular la difusión de mensajes, la comunicación distribuida y la actualización lógica simultánea. A nivel de código, el proceso emisor incrementa su reloj una vez por la acción de difundir, y luego ejecuta peticiones gRPC hacia todos los demás contenedores enviando ese mismo vector.

### Estructura del Escenario Propuesto del Sistema

A partir de las 4 acciones anteriores, se propone un escenario que conste de:
* **Primeras Comunicaciones**: Al inicio del escenario, los procesos simulan eventos internos (selección de asientos, lectura de base de datos vacía) y luego se envían mensajes entre ellos para preparar la transacción.
* **Eventos Paralelos y Procesamiento**: Se llevan a cabo múltiples operaciones al mismo tiempo, por ejemplo el usuario (P1) procesa su pago mientras de fondo el sistema de Emisión (P4) pre-genera folios. Toda la información converge hacia el Orquestador (P5).
* **Difusión de mensajes y Sincronización Final**: Cuando el proceso orquestador (`P5`) confirma el pago y aprueba la orden, difunde un mensaje a todos los procesos para que actualicen su estado final (marcar asientos ocupados en la BD, mandar correo de confirmación, etc.) logrando la consistencia de los relojes.


### Escenario Propuesto: Venta de Boletos de Cine

Estado inicial del vector [P1,P2,P3,P4,P5]: `[0, 0, 0, 0, 0]`

#### Paso 1: Primeras Comunicaciones (Preparación y Selección)

- **A. P1 (App Cliente) - Evento Interno:** El usuario selecciona 2 asientos para "Dune". P1 crea el JSON de intención de compra: `{"cliente": "Marta", "asientos": ["F1", "F2"], "estado": "seleccionando"}`. Incrementa su índice. Vector local: `[1, 0, 0, 0, 0]`.
    
- **B. P1 (App Cliente) - Envío a P5:** P1 manda esta selección al Orquestador para iniciar el trámite. Incrementa su reloj vectorial. Vector local: `[2, 0, 0, 0, 0]`.
    
- **C. P5 (Orquestador) - Recepción de P1:** P5 recibe el JSON y abre una sesión de compra temporal en su memoria. Incrementa su índice (a 1) y toma el máximo. Vector local: `[2, 0, 0, 0, 1]`. Devuelve un ACK.
    
- **D. P2 (Inventario) - Evento Interno:** Rutina de actualización interna. P2 lee su base de datos y confirma que la sala está vacía. Incrementa su índice. Vector local: `[0, 1, 0, 0, 0]`.
    
- **E. P2 (Inventario) - Envío a P4:** P2 le manda un JSON a Emisión: `{"sala": 4, "matriz_asientos": "cargada"}` para avisarle que ya puede generar folios para esa sala. Incrementa su índice. Vector local: `[0, 2, 0, 0, 0]`.
    
- **F. P4 (Emisión) - Recepción de P2:** Recibe la confirmación del Inventario y queda en espera de órdenes. Incrementa su índice (a 1) y toma el máximo. Vector local: `[0, 2, 0, 1, 0]`.
    

#### Paso 2: Eventos Paralelos y Procesamiento de Pago

- **G. P1 (App Cliente) - Evento Interno:** El usuario introduce los datos de su tarjeta de crédito en la interfaz. P1 actualiza su JSON: `{"cliente": "Marta", "monto": 150, "tarjeta": "****1234"}`. Incrementa su índice. Vector local: `[3, 0, 0, 0, 0]`.
    
- **H. P1 (App Cliente) - Envío a P5:** Manda los datos de cobro al Orquestador. Incrementa su índice. Vector local: `[4, 0, 0, 0, 0]`.
    
- **I. P4 (Emisión) - Evento Interno:** Mientras tanto, P4 pre-genera códigos QR en caché para ahorrar tiempo. Incrementa su índice. Vector local: `[0, 2, 0, 2, 0]`.
    
- **J. P5 (Orquestador) - Recepción de P1:** Recibe los datos de la tarjeta de P1. Incrementa su índice (a 2) y toma el máximo. Vector local: `[4, 0, 0, 0, 2]`.
    
- **K. P5 (Orquestador) - Evento Interno:** Se conecta simuladamente al banco, el cobro es exitoso, y genera el dictamen final: `{"orden": "TKT-8899", "estado": "PAGADO"}`. Incrementa su índice. Vector local: `[4, 0, 0, 0, 3]`.
    

#### Paso 3: Difusión de Mensajes (Sincronización Final)

- L. P5 (Orquestador) - Difusión: Envía la orden confirmada a todos los microservicios para que actúen simultáneamente. P5 incrementa su índice una vez por la acción de difundir. Vector local: `[4, 0, 0, 0, 4]`. Manda exactamente este vector a P1, P2, P3 y P4.
    
- **M. P1 (App Cliente) - Recepción de P5:** Recibe la confirmación y muestra en pantalla "Compra Exitosa". Incrementa su índice (a 5) y toma el máximo. Vector local: `[5, 0, 0, 0, 4]`.
    
- **N. P2 (Inventario) - Recepción de P5:** Recibe la orden y cambia el estado de los asientos "F1" y "F2" a "OCUPADO" de forma permanente. Incrementa su índice (a 3) y toma el máximo. Vector local: `[4, 3, 0, 0, 4]`.
    
- **O. P3 (Notificaciones) - Recepción de P5:** Recibe los datos de la compra. Incrementa su índice (a 1) y toma el máximo. Vector local: `[4, 0, 1, 0, 4]`.
    
- **P. P4 (Emisión) - Recepción de P5:** Asigna los QR generados a la orden TKT-8899. Incrementa su índice (a 3) y toma el máximo. Vector local: `[4, 2, 0, 3, 4]`.
    
- **Q. P3 (Notificaciones) - Evento Interno:** Su código extrae el nombre del JSON y simula el envío del correo imprimiendo en consola: _"Enviando boletos a Marta..."_. Incrementa su índice. Vector local final: `[4, 0, 2, 0, 4]`.

A partir del escenario descrito se tiene el siguiente diagrama de eventos:
![Diagrama de Eventos](./SD_Escenario_PF.png)

## Implementación y Ejecución Final

El sistema ha sido implementado exitosamente cumpliendo con los lineamientos establecidos. A continuación se resumen los componentes clave de la implementación:

### Componentes Desarrollados
1. **Contrato gRPC (`IDL.proto`)**: Define los mensajes y los 4 servicios RPC (`EnviarMensaje`, `RecibirMensaje`, `EventoInterno`, `Difusion`). Este archivo se compiló para generar el código base en Python.
2. **Reloj Vectorial (`reloj.py`)**: Implementa la lógica matemática de los relojes de Lamport (incremento local y sincronización `max()` al recibir mensajes) garantizando control de concurrencia mediante hilos y cerrojos (`threading.Lock()`).
3. **Servidor y Cliente RPC (`servidor_grpc.py`, `cliente_grpc.py`)**: Manejan las peticiones de red y la inyección o actualización de los vectores en los mensajes enviados y recibidos. Aquí se formatea y escribe el output en la bitácora (`[INTERNAL]`, `[SEND]`, `[RECEIVE]`, `[BROADCAST]`).
4. **Disparador y Orquestación (`trigger.py`, `main.py`)**: `main.py` inicializa el contenedor con el ID correcto e inicia el servidor. `trigger.py` es una utilidad de línea de comandos usada vía `docker exec` para inyectar transacciones desde afuera.
5. **Infraestructura (`Dockerfile`, `docker-compose.yml`)**: Empaqueta todo en una imagen basada en `python:3.9-slim` y orquesta los 5 procesos (p1 a p5) resolviéndose internamente en la red de Docker `sensores_network`.

### Instrucciones para Ejecutar y Probar

1. **Construir y levantar la infraestructura:**
   ```bash
   sudo docker-compose up -d --build
   ```

2. **Ejecutar la secuencia de la simulación "Venta de Boletos":**
   Usando `trigger.py` desde el host para ordenar los eventos en cada contenedor:
   ```bash
   # Paso 1: Primeras Comunicaciones
   sudo docker exec p1 python src/trigger.py interno
   sudo docker exec p1 python src/trigger.py enviar 5 '{"cliente": "Marta", "asientos": ["F1", "F2"], "estado": "seleccionando"}'
   sudo docker exec p2 python src/trigger.py interno
   sudo docker exec p2 python src/trigger.py enviar 4 '{"sala": 4, "matriz_asientos": "cargada"}'

   # Paso 2: Eventos Paralelos y Procesamiento
   sudo docker exec p1 python src/trigger.py interno
   sudo docker exec p1 python src/trigger.py enviar 5 '{"cliente": "Marta", "monto": 150, "tarjeta": "****1234"}'
   sudo docker exec p4 python src/trigger.py interno
   sudo docker exec p5 python src/trigger.py interno

   # Paso 3: Difusión de Mensajes (Sincronización Final)
   sudo docker exec p5 python src/trigger.py difusion '{"orden": "TKT-8899", "estado": "PAGADO"}'
   sudo docker exec p3 python src/trigger.py interno
   ```

3. **Extraer y Validar las Bitácoras:**
   ```bash
   sudo docker logs p1
   sudo docker logs p2
   sudo docker logs p3
   sudo docker logs p4
   sudo docker logs p5
   ```
   Al revisar los logs, el estado de los vectores coincidirá **exactamente** con todos los vectores estipulados matemáticamente en la sección del escenario (Ej. Vector de P3 finaliza en `[4, 0, 2, 0, 4]`).


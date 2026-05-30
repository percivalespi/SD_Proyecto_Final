# Proyecto Final: Simulación de Procesos Distribuidos
**Sistema de Venta de Boletos de Cine con Relojes Vectoriales**

Este proyecto implementa una simulación de venta de boletos de cine distribuida en 5 procesos Docker. Utiliza gRPC para la conectividad y Relojes Vectoriales de Lamport para mantener el orden de eventos lógicos, junto con bitácoras para auditar la traza de ejecución. 

## Estructura del Proyecto

~~~text
proyecto_distribuidos/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── src/
│   ├── IDL.proto         # Definición de los servicios
│   ├── reloj.py          # Clase del Reloj Vectorial
│   ├── servidor_grpc.py  # Handler de peticiones RPC
│   ├── cliente_grpc.py   # Invocador de peticiones RPC
│   ├── main.py           # Orquestador del contenedor
│   └── trigger.py        # Disparador externo de eventos (CLI)
└── doc/
    ├── notas.md                  # Documentación teórica y escenario detallado
    ├── requerimientos.md         # Requisitos del proyecto
    ├── SD_Escenario_PF.drawio    # Archivo fuente del diagrama (draw.io)
    └── SD_Escenario_PFv1.png     # Imagen del diagrama de espacio-tiempo
~~~

**Funcionamiento de los módulos principales:**
- `reloj.py`: Clase que maneja la lógica matemática del vector (incrementar localmente y aplicar función `max()` al recibir).
- `servidor_grpc.py`: Clase que escucha y procesa peticiones (hereda de `.proto`), formatea logs y actualiza el vector.
- `cliente_grpc.py`: Funciones auxiliares para iniciar conexión asíncrona hacia otros contenedores gRPC.
- `main.py`: Punto de entrada del contenedor. Instancia `reloj.py` en memoria, enciende `servidor_grpc.py` y mantiene el contenedor vivo esperando iteraciones de `trigger.py`.
- `trigger.py`: Herramienta "Control Remoto" usada a través de `docker exec` para activar la simulación enviando órdenes al `main.py`.

---

## ¿Cómo ejecutar el programa?

### Preparación del Entorno Local (Opcional - Para desarrollo)
En caso de realizar modificaciones a `IDL.proto` y requerir recompilarlas en Python, instala las dependencias `grpcio` y `grpcio-tools`:

```bash
# Se recomienda usar un entorno virtual
python -m venv venv
source venv/bin/activate

# Instalación de dependencias:
pip install -r requirements.txt

# Generar clases de gRPC desde la carpeta raíz:
cd src
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. IDL.proto
cd ..
```

### Ejecución con Docker (Orquestación del Clúster)

El sistema completo se ejecuta empaquetado en contenedores aislados.

1. **Construir y levantar la infraestructura:**
   ```bash
   sudo docker-compose down
   sudo docker-compose up -d --build
   ```

2. **Ejecutar la simulación "Venta de Boletos" (Paso a Paso):**
   *Deberás inyectar los eventos al clúster ejecutando los triggers con `docker exec`:*
   ```bash
   # Paso 1: Primeras Comunicaciones (Selección de boletos)
   sudo docker exec p1 python src/trigger.py interno
   sudo docker exec p1 python src/trigger.py enviar 5 '{"cliente": "Victor", "asientos": ["F1", "F2"], "estado": "seleccionando"}'
   sudo docker exec p2 python src/trigger.py interno
   sudo docker exec p2 python src/trigger.py enviar 4 '{"sala": 4, "matriz_asientos": "cargada"}'

   # Paso 2: Eventos Paralelos y Procesamiento (Pago del usuario)
   sudo docker exec p1 python src/trigger.py interno
   sudo docker exec p1 python src/trigger.py enviar 5 '{"cliente": "Victor", "monto": 150, "tarjeta": "****1234"}'
   sudo docker exec p4 python src/trigger.py interno
   sudo docker exec p5 python src/trigger.py interno

   # Paso 3: Difusión y Sincronización Final (Confirmación de compra)
   sudo docker exec p5 python src/trigger.py difusion '{"orden": "TKT-1000", "estado": "PAGADO"}'
   sudo docker exec p3 python src/trigger.py interno
   ```

3. **Extraer bitácoras (Validación Matemática):**
   ```bash
   sudo docker logs p1
   sudo docker logs p2
   sudo docker logs p3
   sudo docker logs p4
   sudo docker logs p5
   sudo docker-compose logs --tail=50
   ```

---

## Fases del Desarrollo (Progreso)

### Fase 1: Definición y Contratos (COMPLETADA)
- [x] Contrato gRPC: Definir los 4 servicios requeridos (envío, recepción, evento interno y difusión) en `src/IDL.proto`.  
- [x] Compilación: Ejecutar `grpcio-tools` para generar las clases autogeneradas en Python.
- [x] Diseño del Escenario: Finalizar el diagrama espacio-tiempo documentando la Venta de Boletos de Cine con 5 microservicios (`doc/notas.md`).

### Fase 2: Lógica de la Aplicación en Python (COMPLETADA)
- [x] El Estado (`src/reloj.py`): Implementar vector concurrente con operaciones `max()`.
- [x] El Oyente (`src/servidor_grpc.py`): Recepción RPC escribiendo registros estructurados `[INTERNAL]`, `[SEND]` y `[RECEIVE]`.
- [x] El Hablador (`src/cliente_grpc.py`): Funcionalidad de envíos simples y modalidad Broadcast hacia todos los miembros.
- [x] El Orquestador (`src/main.py`): Inyección de entorno Docker a la lógica e inicio de servidor persistente en cada contenedor.
- [x] El Disparador (`src/trigger.py`): Control remoto CLI.

### Fase 3: Infraestructura Docker (COMPLETADA)
- [x] Empaquetado: Configuración de `Dockerfile` empaquetando entorno Python-Slim.
- [x] Red Virtual: Orquestación mediante `docker-compose.yml` resolviendo hostnames hacia la red `boletos_network`.

### Fase 4: Pruebas y Entregables (COMPLETADA)
- [x] Ejecución: Disparo iterativo mediante `docker exec` inyectando todo el escenario teórico.
- [x] Validación cruzada: Obtención de logs para demostrar cómo los vectores cuadran idénticamente contra el diagrama de diseño.
- [ ] Demostración audiovisual: Pendiente la realización de la grabación de pantalla del terminal para la evaluación final con la profesora.

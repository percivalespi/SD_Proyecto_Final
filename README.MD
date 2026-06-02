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
│   └── trigger.py        # Disparador externo de eventos
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
   sudo docker --version
   sudo docker-compose --version
   sudo docker-compose down
   sudo docker-compose up -d --build
   sudo docker-compose ps
   ```

2. **Ejecutar la simulación "Venta de Boletos" (Paso a Paso):**
   *Deberás inyectar los eventos al clúster ejecutando los triggers con `docker exec`:*
   ```bash
   # Fase 1: Primeras Comunicaciones (Selección de boletos)
   sudo docker exec p1 python src/trigger.py interno
   sudo docker exec p1 python src/trigger.py enviar 5 '{"cliente": "Victor", "asientos": ["F1", "F2"], "estado": "seleccionando"}'
   sudo docker exec p2 python src/trigger.py interno
   sudo docker exec p2 python src/trigger.py enviar 4 '{"sala": 4, "matriz_asientos": "cargada"}'

   # Fase 2: Eventos Paralelos y Procesamiento (Pago del usuario)
   sudo docker exec p1 python src/trigger.py interno
   sudo docker exec p1 python src/trigger.py enviar 5 '{"cliente": "Victor", "monto": 150, "tarjeta": "****1234"}'
   sudo docker exec p4 python src/trigger.py interno
   sudo docker exec p5 python src/trigger.py interno

   # Fase 3: Difusión y Sincronización Final (Confirmación de compra)
   sudo docker exec p5 python src/trigger.py difusion '{"orden": "TKT-1000", "estado": "PAGADO"}'
   sudo docker exec p3 python src/trigger.py interno
   ```

3. **Extraer bitácoras:**
   ```bash
   sudo docker logs p1
   sudo docker logs p2
   sudo docker logs p3
   sudo docker logs p4
   sudo docker logs p5
   sudo docker-compose logs --tail=50
   ```
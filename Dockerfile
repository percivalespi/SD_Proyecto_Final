FROM python:3.9-slim

WORKDIR /app

# Copiamos las dependencias
COPY requirements.txt .

# Instalamos grpcio y grpcio-tools
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el código fuente
COPY src/ /app/src/

# Añadimos /app/src al path para que Python encuentre los módulos autogenerados
ENV PYTHONPATH=/app/src

# Arrancamos el orquestador
CMD ["python", "src/main.py"]
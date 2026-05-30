FROM python:3.9-slim
# Estableciendo el directorio de trabajo dentro del contenedor
WORKDIR /app

# Dependencias necesarias para gRPC
COPY requirements.txt .

# Instalcion de las depencias: grpcio y grpcio-tools
RUN pip install --no-cache-dir -r requirements.txt

# Copiaa del código fuente al contenedor
COPY src/ /app/src/

# Añadiendo al path de Python el directorio con el código fuente
ENV PYTHONPATH=/app/src

# Inicialización del proceso de acuerdo a su ID, este se pasa como argmento
CMD ["python", "src/main.py"]
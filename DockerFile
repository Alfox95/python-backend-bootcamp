# Imagen base con Python 3.12
FROM python:3.12.10-slim

# Evita que Python cree archivos .pyc
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiamos requirements.txt primero para aprovechar cache
COPY requirements.txt .

# Instalamos dependencias
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos todo el código del proyecto
COPY . .

# Puerto que usa Render para Web Services
ENV PORT=10000

# Comando para arrancar la app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]
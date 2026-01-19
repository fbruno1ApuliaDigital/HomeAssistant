FROM python:3.9-slim
WORKDIR /app
COPY simulator.py .
RUN pip install paho-mqtt
CMD ["python", "simulator.py"]
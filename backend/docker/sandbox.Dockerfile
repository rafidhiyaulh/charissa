FROM python:3.11-slim

RUN pip install --no-cache-dir pandas numpy matplotlib

COPY sandbox_server.py /sandbox_server.py
COPY sandbox_client.py /sandbox_client.py

CMD ["python", "/sandbox_server.py"]

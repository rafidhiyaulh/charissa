FROM python:3.11-slim

RUN pip install --no-cache-dir pandas numpy matplotlib

COPY sandbox_server.py /sandbox_server.py

EXPOSE 8765

CMD ["python", "/sandbox_server.py"]

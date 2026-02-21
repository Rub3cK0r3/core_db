FROM python:3.12-slim
WORKDIR /app
COPY deploy/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ /app
ENV PYTHONPATH=/app:$PYTHONPATH
CMD ["python", "-m", "processor.main"]

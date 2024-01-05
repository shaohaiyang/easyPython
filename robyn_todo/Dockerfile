#FROM python:3.11-bookworm
FROM python:3.10-slim

RUN  mkdir -p /app
WORKDIR /app
COPY src/* .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

RUN python3 -m prisma generate
RUN python3 -m prisma migrate dev --name init

EXPOSE 8080

CMD ["python3", "app.py", "--log-level=DEBUG"]

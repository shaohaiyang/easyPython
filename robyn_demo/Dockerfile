#FROM python:3.10-slim
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir --upgrade -r requirements.txt
RUN python3 -m prisma generate
RUN python3 -m prisma migrate demo --name init

EXPOSE 8080

CMD ["python3", "app.py", "--log-level=ERROR"]

#docker build -t robyn_demo --rm .
#docker run -tid --name=robyn_demo -v /src:/app -p 4000:8080 robyn_demo sh -c "prisma db push --schema /app/schema.prisma && python3 /app/app.py --log-level=ERROR"

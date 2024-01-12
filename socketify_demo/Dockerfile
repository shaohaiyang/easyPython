#FROM python:3.10-slim
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir --upgrade -r requirements.txt
RUN python3 -m prisma generate
RUN apt-get update && apt-get install -y --no-install-recommends \
libuv1 \
zlib1g \
&& \
apt-get clean && \
rm -rf /var/lib/apt/lists/*

EXPOSE 8080

CMD ["tail", "-f", "/dev/null"]

#docker build -t socketify_py311 --rm .
#docker run -tid --name=socketify_demo -v /src:/app -p 4000:8080 socketify_py311 sh -c "prisma db push --schema schema.prisma && python3 app.py --workers 4"

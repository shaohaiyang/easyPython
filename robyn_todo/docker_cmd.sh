#docker build -t robyn_todo --rm .
docker run -tid --name=robyn_todo -v /root/robyn_todo/src:/app -p 4000:8080 \
      robyn_todo sh -c "prisma db push --schema /app/schema.prisma && python3 /app/app.py"

FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Environment variables for service networking
ENV MYSQL_HOST=mysql_db
ENV MYSQL_USER=root
ENV MYSQL_PASSWORD=12345
ENV MYSQL_DB=inventory_db
ENV MONGO_URI=mongodb://mongo_db:27017/

EXPOSE 5000

CMD ["python", "src/app.py"]

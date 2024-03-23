FROM python:3.8.18

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5004

CMD ["python", "app.py"]

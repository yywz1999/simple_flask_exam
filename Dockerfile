FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.ustc.edu.cn/pypi/web/simple
RUN mkdir -p instance

COPY . .

ENV FLASK_APP app.py
ENV FLASK_ENV production
ENV FLASK_SECRET_KEY your-secret-key-here
ENV SECRET_KEY your-secret-key-here
ENV DATABASE_URL sqlite:////instance/test.db

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]

FROM python:3.10-alpine

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ARG TOKEN
ARG IG_LOGIN
ARG IG_PASSWORD
ENV BOT_TOKEN=$BOT_TOKEN
ENV IG_LOGIN=$IG_LOGIN
ENV IG_PASSWORD=$IG_PASSWORD
# Установим директорию для работы

WORKDIR /passiora_qr_bot

COPY ./requirements.txt ./

# Устанавливаем зависимости и gunicorn
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r ./requirements.txt

# Копируем файлы и билд
COPY ./ ./

RUN chmod -R 777 ./
# more https://proghunter.ru/articles/python-bot-with-chatgpt-dockerization-and-deployment-to-vps-guide

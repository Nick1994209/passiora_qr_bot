FROM python:3.10

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV TOKEN {$TOKEN}
# Установим директорию для работы

WORKDIR /passiora_qr_bot

COPY ./requirements.txt ./

# Устанавливаем зависимости и gunicorn
RUN pip install --upgrade pip && pip install -r requirements.txt

# Копируем файлы и билд
COPY ./ ./

RUN chmod -R 777 ./
RUN chmod +x ./
EXPOSE 5000
STOPSIGNAL SIGTERM
# more https://proghunter.ru/articles/python-bot-with-chatgpt-dockerization-and-deployment-to-vps-guide
ENTRYPOINT ["python3", "main.py"]
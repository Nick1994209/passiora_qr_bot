FROM python:3.10


ENV TOKEN {$TOKEN}
# Установим директорию для работы

WORKDIR /passiora_qr_bot

COPY ./requirements.txt ./

# Устанавливаем зависимости и gunicorn
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r ./requirements.txt

# Копируем файлы и билд
COPY ./ ./

RUN chmod -R 777 ./
EXPOSE 5000

# more https://proghunter.ru/articles/python-bot-with-chatgpt-dockerization-and-deployment-to-vps-guide
CMD ["python3", "main.py"]
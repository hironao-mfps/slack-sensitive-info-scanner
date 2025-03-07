FROM python:3.9-slim

WORKDIR /app

RUN pip install slack-bolt python-dotenv

COPY minimal_bot_v2.py ./minimal_bot.py

CMD ["python", "-u", "minimal_bot.py"]

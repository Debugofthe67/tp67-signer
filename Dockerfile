FROM nullx0/zsign
# This uses the image YOU found as the base
RUN apt-get update && apt-get install -y python3 python3-pip
RUN pip3 install python-telegram-bot requests
COPY . .
CMD ["python3", "bot.py"]

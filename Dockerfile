FROM python:3.10.6

1. Create app directory

RUN mkdir /bot && chmod 777 /bot WORKDIR /bot

2. Avoid interactive prompts

ENV DEBIAN_FRONTEND=noninteractive

3. Install system dependencies

RUN apt -qq update && 
apt -qq install -y git wget pv jq python3-dev ffmpeg mediainfo neofetch && 
apt-get install -y wget -f && 
apt-get install -y fontconfig -f

4. Install Python dependencies

Copy only requirements first for better caching

COPY requirements.txt . RUN pip3 install --no-cache-dir -r requirements.txt

Ensure python-telegram-bot is installed in case it's missing from requirements

RUN pip3 install --no-cache-dir python-telegram-bot

5. Copy application code

COPY . .

6. Default command

CMD ["bash", "run.sh"]


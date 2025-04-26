FROM python:3.10.6

# System setup
RUN apt-get update && \
    apt-get install -y \
    git \
    wget \
    ffmpeg \
    mediainfo \
    fontconfig \
    && rm -rf /var/lib/apt/lists/*

# Application setup
WORKDIR /bot
COPY . .
RUN pip3 install --no-cache-dir -r requirements.txt

# Permissions and cleanup
RUN chmod +x run.sh

CMD ["bash", "run.sh"]

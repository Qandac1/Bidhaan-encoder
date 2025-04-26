FROM python:3.10.6-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
    ffmpeg \
    mediainfo \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /bot
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create run script
RUN echo '#!/bin/bash\npython3 bot.py' > run.sh && \
    chmod +x run.sh

CMD ["./run.sh"]

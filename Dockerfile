FROM apache/airflow:3.3.1

USER root

RUN apt-get update && \
    apt-get install -y \
    libgtk-3-0 \
    libdbus-glib-1-2 \
    libasound2 \
    libnss3 \
    libx11-xcb1 \
    libxtst6 \
    libxrandr2 \
    libgbm1 \
    libdrm2 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libatspi2.0-0 \
    libcups2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libxkbcommon0 \
    ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow

COPY requirements.txt /requirements.txt

RUN pip install --no-cache-dir -r /requirements.txt

RUN python -m camoufox fetch
RUN python -m playwright install firefox 
FROM python:3.11-slim

# Install necessary OS packages
RUN apt-get update && \
    apt-get install -y graphviz wkhtmltopdf && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

ADD requirements.txt /app/
ADD packages.txt /app/
RUN pip install -r requirements.txt

ADD . /app

#Run the application on port 8080
ENTRYPOINT ["streamlit", "run", "app.py", "--theme.primaryColor=#005cb9", "--server.port=8080", "--server.enableCORS=false", "--server.enableWebsocketCompression=false", "--server.address=0.0.0.0"]
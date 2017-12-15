FROM python:3-alpine
WORKDIR /app
ADD requirements.txt /app
RUN pip install -r requirements.txt
ADD . /app
ENTRYPOINT ["python", "exporter.py"]
EXPOSE 9595

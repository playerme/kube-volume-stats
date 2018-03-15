FROM python:3-alpine
WORKDIR /app
ADD requirements.txt /app
RUN pip install -r requirements.txt
ADD . /app
CMD ["python", "exporter.py"]
EXPOSE 9595

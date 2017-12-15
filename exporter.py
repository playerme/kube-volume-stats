import os
import logging
from flask import Flask
from metrics import latest_data, scheduler

logging.basicConfig(level=logging.os.environ.get('LOG_LEVEL', 'INFO'))
SERVICE_PORT = int(os.environ.get('SERVICE_PORT', 9595))
app = Flask(__name__)

@app.route('/metrics')
def metrics():
    return latest_data()


if __name__ == '__main__':
    scheduler.start()
    app.run(host="0.0.0.0", port=SERVICE_PORT, threaded=True, debug=True)


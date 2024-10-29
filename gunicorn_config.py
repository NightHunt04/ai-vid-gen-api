# gunicorn_config.py

timeout = 1000  # max 1800 seconds/30 minutes on Render

workers = 1
threads = 4

bind = "0.0.0.0:10000"

loglevel = "info"
accesslog = "-"
errorlog = "-"

graceful_timeout = timeout
keepalive = 65
import os

port = int(os.environ.get('PORT', 10000))
bind = f"0.0.0.0:{port}"
workers = 2  # Reduzindo o número de workers
timeout = 120
preload_app = True
accesslog = '-'
errorlog = '-' 
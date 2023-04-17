workers = 4
bind = "0.0.0.0:3000"
wsgi_app = "app:app"
accesslog = "gunicorn.log"
errorlog = "gunicorn.log"


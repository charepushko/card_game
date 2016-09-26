#! /usr/bin/python
# from flask_socketio import SocketIO
from app import app

# socketio = SocketIO(app)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
#    socketio.run(app, use_reloader=True)

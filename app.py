import bottle
import controllers

app = bottle.app()
application = app
bottle.debug(True)

if __name__=='__main__':
    bottle.debug(True)
    bottle.run(app=app, host='0.0.0.0', reloader=True)

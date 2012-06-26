from bottle import route, run, debug, request, response, get, post
import json

@get('/test')
def test():
    print request.headers.keys()
    print request.query.keys()
    print request.forms.keys()
    print request.params.keys()
    print request.json
    print request.body.read()
    return "Hello again! " #+ request.query.ecky


debug(True)
run(host='0.0.0.0', reloader=True)

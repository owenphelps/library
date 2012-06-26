from bottle import route, run, debug, request, response, get, post
import json
from library_model import Book


def load_books():
    json_books = [json.loads(x) for x in open('library.json', 'r').read().splitlines()]
    books = [Book(j['title'], j.get('description', ''), j['ISBN']) for j in json_books]
    return books

all_books = load_books()

@get('/test')
def test():
    print request.headers.keys()
    print request.query.keys()
    print request.forms.keys()
    print request.params.keys()
    print request.json
    print request.body.read()
    return "Hello again!"

def get_prefix(request):
    urlparts = request.urlparts
    return "%s://%s/library/api" % (urlparts[0], urlparts[1])

@get('/library/api/')
@get('/library/api')
def library():
    prefix = get_prefix(request)
    return dict(
        books=prefix + "/books",
        users=prefix + "/users"
        )

@get('/library/api/books/<book_id>')
@get('/library/api/books/')
@get('/library/api/books')
def books(book_id=None):
    response.set_header('Content-Type', 'application/json')
    prefix = get_prefix(request)
    if book_id:
        the_book = None
        for bk in all_books:
            if bk.isbn == book_id:
                the_book = bk
                break
        if the_book:
            return bk.to_json(prefix=prefix)
        else:
            response.set_header('Content-Type', 'text/html')
            response.status = 404
    else:
        bks = [bk.to_json(prefix=prefix) for bk in all_books]

        return '[' + ',\n'.join(bks) + ']'

debug(True)
run(host='0.0.0.0', reloader=True)


LIBRARY
=======

The main entry point to the library service.


BOOK
====

The `book` element MUST contain `title`, `description`, `isbn`. MAY contain
`thumbnail_url`, `borrower` or `reservers`.

Data
----

* `title`
* `description`
* `isbn`
* `thumbnail_url`
* `borrower`
* `reservers`

Links
-----

* `reserve`
* `borrow`
* `return`
* `cancel`

Example
-------

    {
        "title": "My first book",
        "description": "The first book I ever wrote.",
        "isbn": "1234567890",
        "borrower": "A person",
        "reservers": ['Another person', 'And another']
        _links:
        {
            'borrow': {'href': '...'}, 'title': 'Use this to borrow the book.',
            'reserve': {'href': '...'}, 'title': 'Use this to reserve the book.'
        }
    }


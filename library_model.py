#!/usr/bin/env python
import json

# ----------------------------------------------------------------------

class AlreadyOnLoanError(Exception): pass
class BorrowingWhileReservedError(Exception): pass
class NotReservedError(Exception): pass
class NotCheckedOutError(Exception): pass
class NotTheBorrowerError(Exception): pass

# ----------------------------------------------------------------------

def equivalent_lists(first, second):
    assert_equals(sorted(first), sorted(second))

# ----------------------------------------------------------------------

class Book(object):
    BORROWED  = 'borrowed'
    AVAILABLE = 'available'

    CAN_RESERVE = 'can_reserve'
    CAN_BORROW  = 'can_borrow'
    CAN_RETURN  = 'can_return'
    CAN_CANCEL  = 'can_cancel'

    def __init__(self, title, description, isbn, borrower='', reservations=None):
        self.title = title
        self.description = description
        self.isbn = isbn
        self.borrower = borrower
        self.reservations = reservations or []
        
    def reserve(self, reserver):
        assert reserver and reserver.strip() != ''
        if not reserver in self.reservations:
            self.reservations.append(reserver)

    def un_reserve(self, reserver):
        assert reserver and reserver.strip() != ''
        if not reserver in self.reservations:
            raise NotReservedError('Not reserved by this user')
        self.reservations.remove(reserver)

    def check_out(self, borrower):
        assert borrower and borrower.strip() != ''

        if self.status() == Book.BORROWED:
            raise AlreadyOnLoanError('Already on loan')

        if self.reservations:
            if self.reservations[0] == borrower:
                self.reservations.pop(0)
            else:
                raise BorrowingWhileReservedError('Book is reserved')

        self.borrower = borrower

    def check_in(self, borrower):
        assert borrower and borrower.strip() != ''
        if self.status() != Book.BORROWED:
            raise NotCheckedOutError('Book is not checked out')
        if self.borrower != borrower:
            raise NotTheBorrowerError('User did not check out this book')

        self.borrower = ''

    def status(self):
        if self.borrower:
            return Book.BORROWED
        else:
            return Book.AVAILABLE

    def get_options(self, for_user):
        options = {}
        is_borrower       = self.borrower != '' and for_user == self.borrower
        is_reserver       = for_user in self.reservations
        is_first_reserver = is_reserver and self.reservations[0] == for_user

        options[Book.CAN_RESERVE] = not(is_borrower or is_reserver)
        options[Book.CAN_BORROW] = (is_first_reserver or not self.reservations) and not self.borrower
        options[Book.CAN_RETURN] = is_borrower
        options[Book.CAN_CANCEL] = is_reserver

        # Only return true values (makes using things easier).
        for key in options.keys():
            if not options[key]: options.pop(key) 
        return options

    def links(self, for_user='', prefix=''):
        ret = []
        options = self.get_options(for_user)

        ret.append(dict(rel='self', href=prefix + '/books/' + self.isbn))

        if options.get(Book.CAN_RESERVE, False):
            ret.append(dict(rel='reserve', href=prefix + '/books/' + self.isbn + '/reservations'))

        if options.get(Book.CAN_BORROW, False):
            ret.append(dict(rel='borrow', href=prefix + '/books/' + self.isbn + '/borrower'))

        if options.get(Book.CAN_RETURN, False):
            ret.append(dict(rel='return', href=prefix + '/books/' + self.isbn + '/return'))

        if options.get(Book.CAN_CANCEL, False):
            ret.append(dict(rel='cancel', href=prefix + '/books/' + self.isbn + '/reservations/' + for_user + '/cancel'))

        return ret

    def to_json(self, for_user='', prefix=''):
        js = dict(title=self.title,
                  description=self.description,
                  isbn=self.isbn,
                  borrower=self.borrower,
                  reservations=self.reservations,
                  _links=self.links(for_user, prefix))
        return json.dumps(js, indent=2)

# ----------------------------------------------------------------------

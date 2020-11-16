from time import time
# inherits from printable class to print out blockchain
from utility.printable import Printable


class Block(Printable):

    def __init__(self, index, previous_hash, transactions, proof, timestamp=None):
        self.index = index
        self.previous_hash = previous_hash
        # timestamp = current time if no timestamp value is passed to the constructor
        # this is so because default arguments are evaluated once hence it will be the
        # same value every time the constructor is called
        # default arguments are evaluated only once in python
        # single underscore before a variable name in python means the variable is private
        self.timestamp = time() if timestamp is None else timestamp
        self.transactions = transactions
        self.proof = proof

from collections import OrderedDict
# inherits from printable class to print out blockchain
from utility.printable import Printable


class Transaction(Printable):

    """A transaction which can be added to a block in the blockchain

        Attributes:
            :sender: The sender of the coins.
            :recipient: The recipient of the coins.
            :signature: The signature of the transaction
            :amount: The amount of coins that was sent.

    """

    def __init__(self, sender, recipient, signature, amount):
        self.sender = sender  # sender is the public key
        self.recipient = recipient
        self.amount = amount
        self.signature = signature

    # function to turn the transaction object to an ordered dict

    def to_ordered_dict(self):
        return OrderedDict([('senser', self.sender), ('recipient', self.recipient), ('signature', self.signature), ('amount', self.amount)])

"""Provides verification helper methods"""

from utility.hash_util import hash_block, hash_string_256
from wallet import Wallet


class Verification:

    # A class method belongs to the class and takes the cls keyword as it's first argument.
    # This is not an instance method and can't be used by objects but the class itself.
    @classmethod
    def verify_chain(cls, blockchain):
        """Verify the current blockchain and return True if it's valid, False if it's not"""
        for index, block in enumerate(blockchain):  # enumerate returns index and value of a list
            if index == 0:
                continue
            if block.previous_hash != hash_block(blockchain[index - 1]):
                print("wrong hash")
                return False
            if not cls.valid_proof(block.transactions[:-1], block.previous_hash, block.proof):
                print('Proof of work is invalid')
                return False
        return True

    # A static method belongs to the class but doesn't take cls as the first argument and doesn't use any of the class's members

    @staticmethod
    # pass in get_balance fuctions as an input
    def verify_transaction(transaction, get_balance, check_funds=True):
        """Verify if sender has a enough to send transaction amount"""
        # check to see that the sender's balance can cover the transaction amount and that the signatures match for each transaction
        if check_funds:
            sender_balance = get_balance(transaction.sender)
            return sender_balance >= transaction.amount and Wallet.verify_transaction(transaction)
        else:
            return Wallet.verify_transaction(transaction)

    @classmethod
    def verify_transactions(cls, open_transactions, get_balance):
        """Verifies all open transactions"""
        # make sure all results are true for verifying each transaction in open_transactions
        return all([cls.verify_transaction(tx, get_balance, False) for tx in open_transactions])

    @staticmethod
    def valid_proof(transactions, last_hash, proof):
        """To validate a proof of work number and see if it solves the puzzle algorithm

        Arguments:
            :transactions: The transactions of the block for which the proof is being generated for
            :last_hash: The previous blocks hash which will be stored in the current block
            :proof: The proof number we're testing
        """
        # create a string with all the hash inputs
        guess = (str([tx.to_ordered_dict() for tx in transactions]
                     ) + str(last_hash) + str(proof)).encode()
        # hash the string
        # IMPORTANT: This is NOT the hash as will be stored in the previous_hash. It's not a blocks hash, it's just to get the proof
        guess_hash = hash_string_256(guess)
        # print(guess_hash)
        # only a hash which starts with two zeros will pass the return condition
        return guess_hash[0:2] == '00'

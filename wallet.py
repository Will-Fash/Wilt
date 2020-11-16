# RSA to create wallets i.e. public/private key pairs
from Crypto.PublicKey import RSA
# pkcs1_15 to generate signatures
from Crypto.Signature import pkcs1_15
# SHA256 to generate hash
from Crypto.Hash import SHA256
# Random to generate random odd and positive integer for the RSA generate method
import Crypto.Random
# binascii to convert binary to string and vice versa
import binascii


class Wallet:
    def __init__(self, node_id):
        self.private_key = None
        self.public_key = None
        self.node_id = node_id

    # create keys using the generate keys function

    def create_keys(self):
        private_key, public_key = self.generate_keys()
        self.private_key = private_key
        self.public_key = public_key

    # save keys to file.

    def save_keys(self):
        if self.public_key != None and self.private_key != None:
            try:
                with open(f'wallet-{self.node_id}.txt', mode='w') as f:
                    f.write(self.public_key)
                    # line break will be part of firstline and will be added to the end of firstline
                    f.write("\n")
                    f.write(self.private_key)
                return True
            except(IOError, IndexError):
                print('Saving wallet failed...')
                return False

    # load keys from file

    def load_keys(self):
        try:
            with open(f'wallet-{self.node_id}.txt', mode='r') as f:
                # reads all data in the file using the same structure as the file was written
                keys = f.readlines()
                # to select public key without the line break character
                public_key = keys[0][:-1]
                private_key = keys[1]
                self.public_key = public_key
                self.private_key = private_key
                return True  # if load keys works
        except(IOError, IndexError):
            print("Loading wallet failed...")
            return False  # if load keys fails

    # generating public and private keys

    def generate_keys(self):
        private_key = RSA.generate(1024, Crypto.Random.new().read)
        public_key = private_key.publickey()
        # binascii hexlify to convert keys to string
        return (binascii.hexlify(private_key.exportKey('DER')).decode('ascii'), binascii.hexlify(public_key.exportKey('DER')).decode('ascii'))

    # to sign transactions so that open transactions that aren't in the blockchain yet can't be manipulated

    def sign_transaction(self, sender, recipient, amount):
        # use binascii unhexlify to convert string back to keys as our keys are now strings
        signer = pkcs1_15.new(RSA.importKey(
            binascii.unhexlify(self.private_key)))
        h = SHA256.new((str(sender) + str(recipient) +
                        str(amount)).encode('utf8'))
        # sign the hash of the message contained in variable "h"
        signature = signer.sign(h)
        # return signature in string as it is binary by default
        return binascii.hexlify(signature).decode('ascii')

    # this will verify

    @staticmethod
    def verify_transaction(transaction):
        public_key = RSA.importKey(binascii.unhexlify(transaction.sender))
        # to verify if corresponding private key signed this transaction
        verifier = pkcs1_15.new(public_key)
        h = SHA256.new((str(transaction.sender) + str(transaction.recipient) +
                        str(transaction.amount)).encode('utf8'))
        try:
            # binascii.unhexlify to convert back to bits from string
            if verifier.verify(h, binascii.unhexlify(transaction.signature)) == None:
                return True
        except (ValueError, TypeError):
            return False

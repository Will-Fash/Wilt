import hashlib as hl
import json

# all variable to limit what can be imported from this file
#__all__ = ['hash_string_256', 'hash_block']


def hash_string_256(string):
    return hl.sha256(string).hexdigest()


def hash_block(block):
    """To calculate the hash of a block for verification
    Arguments:
        block : The block to hashed
    """
    # hashlib method sha.256 to generate a hash code, method only works on string
    # hence we use dumps method from json lib to convert dict like object to string
    # we also have to encode to proper string(utf-8 is default).
    # we have to use hexdigest method to turn hashcode to string else return
    # type will be byte
    # sort keys is true in order to avoid the order of dictionaries changing
    # as this can cause a different hash to be produced for the same exact input
    # json only works for a limited set of python datatypes, it doesn't work for objects and now that we've create a block object json wouldn't work anymore
    # the copy so we dont have to manipulate the block chain from in here
    hashable_block = block.__dict__.copy()
    hashable_block['transactions'] = [tx.to_ordered_dict()
                                      for tx in hashable_block['transactions']]
    return hash_string_256(json.dumps(hashable_block, sort_keys=True).encode())

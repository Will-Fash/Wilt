# ordered dict so that all keys are ordered and a change in ordering won't
# lead to a different hashvalue
# from collections import OrderedDict
from functools import reduce
from utility.hash_util import hash_block
import hashlib as hl
import pickle
import json
from block import Block
from transaction import Transaction
from utility.verification import Verification
from wallet import Wallet
import requests

# The reward we give to miners (for creating a new block)
MINING_REWARD = 10


class Blockchain:
    def __init__(self, public_Key, node_id):
        # Our starting block for the blockchain
        genesis_block = Block(0, "", [], 100, 0)
        # Initializing our (empty) blockchain list
        self.chain = [genesis_block]
        # Unhandled tranactions
        self.__open_transactions = []
        # Set of participants in the network
        self.__peer_nodes = set()
        # id of the node where the blockchain is being hosted
        self.public_Key = public_Key
        # if there's data onfile load it
        self.node_id = node_id
        self.resolve_conflict = False
        self.load_data()

    # getter method for property "chain"

    @property
    def chain(self):
        return self.__chain[:]

    # setter method for chain

    @chain.setter
    def chain(self, val):
        self.__chain = val

    def get_open_transactions(self):
        return self.__open_transactions[:]

    def load_data(self):
        try:  # try and catch block to prevent application crashes
            with open(f'blockchain-{self.node_id}.txt', mode='r') as f:
                # rb mode to read a binary file because pickle writes in binary and file type is .p
                f_content = f.readlines()
                # blockchain = f_content['chain']
                # open_transactions = f_content['ot']
                blockchain = json.loads(f_content[0][:-1])
                updated_blockchain = []
                for block in blockchain:  # reading data from file and storing it in an ordereddict because orderedict is part of the last hash but isn't saved on file
                    converted_tx = [Transaction(
                        tx['sender'], tx['recipient'], tx['signature'], tx['amount']) for tx in block['transactions']]
                    #      for tx in block['transactions']] "previous transactions with orderded dict before the trasaction class was created"
                    updated_block = Block(
                        block['index'], block['previous_hash'], converted_tx, block['proof'], block['timestamp'])
                    updated_blockchain.append(updated_block)
                self.chain = updated_blockchain  # using the setter to set the chain's values
                open_transactions = json.loads(f_content[1][:-1])
                updated_transactions = []
                for tx in open_transactions:
                    updated_transaction = Transaction(
                        tx['sender'], tx['recipient'], tx['signature'], tx['amount'])
                    #transaction = OrderedDict([('sender', tx['sender']),('recipient', tx['recipient']),('amount', tx['amount'])])
                    # above former transactions before using the transaction class
                    updated_transactions.append(updated_transaction)
                self.__open_transactions = updated_transactions
                peer_nodes = json.loads(f_content[2])
                self.__peer_nodes = set(peer_nodes)
        except (IOError, IndexError):  # Handle expected errors
            pass
        finally:  # Always runs regardless
            print('Cleanup!')

    def save_data(self):
        try:
            with open(f'blockchain-{self.node_id}.txt', mode='w') as f:
                # wb mode writes binary data when using pickle, text is default so w works but you can use 'wt'
                # file type is .p for pickle
                # code below could also be done as json.dump(data_to_store,f)
                saveable_chain = [block.__dict__ for block in [Block(block_el.index, block_el.previous_hash, [
                                                                     tx.__dict__ for tx in block_el.transactions], block_el.proof, block_el.timestamp) for block_el in self.__chain]]  # the nested list is so that we can save it with json
                # save the chain to the blockchain.txt file
                f.write(json.dumps(saveable_chain))
                f.write('\n')
                # this so that we can save with json, dict to create dictionary snapshot of the transactions in open transactions
                saveable_tx = [tx.__dict__ for tx in self.__open_transactions]
                # save the open transactions to the blockchain.txt file
                f.write(json.dumps(saveable_tx))
                f.write('\n')
                f.write(json.dumps(list(self.__peer_nodes)))
                # use a dictionary when pickling data
                # save_data = {
                #     'chain': blockchain,
                #     'ot': open_transactions
                # }
                # f.write(pickle.dumps(save_data))
        except IOError:
            print('Saving failed!')

    def proof_of_work(self):
        """ Generate a proof of work for the open transactions, the hash of the previous block and the proof number """
        last_block = self.__chain[-1]
        last_hash = hash_block(last_block)
        proof = 0
        while not Verification.valid_proof(self.__open_transactions, last_hash, proof):
            proof += 1
        return proof

    def get_balance(self, sender=None):
        """
        Get balance for a participant by calulating how much is sent
        and how much is recieved and getting the difference between 
        inflow and outflow.
        """
        # Check if self.public_Key equals none and return nothing from get balance
        if sender == None:
            if self.public_Key == None:
                return None
            # participant is the id of the node who owns this blockchain
            participant = self.public_Key
        else:
            participant = sender
        # Fetch a list of all sent coins for a given person
        tx_sender = [[tx.amount for tx in block.transactions
                      if tx.sender == participant] for block in self.__chain]

        # This fetches sent amounts of open transactions (to avoid double spending)
        open_tx_sender = [
            tx.amount for tx in self.__open_transactions if tx.sender == participant]
        tx_sender.append(open_tx_sender)
        # print(tx_sender)

        # Calculate amount sent
        amount_sent = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt)
                             if len(tx_amt) > 0 else tx_sum + 0, tx_sender, 0)

        # This fetches received coin amounts of transactions that are already in the blockchain
        # We ignore open transactions here because you shouldn't be able to spend
        tx_recipient = [[tx.amount for tx in block.transactions
                         if tx.recipient == participant] for block in self.__chain]

        # Calculate amount recvd
        amount_recvd = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt)
                              if len(tx_amt) > 0 else tx_sum + 0, tx_recipient, 0)

        # return total balance
        return amount_recvd - amount_sent

    def get_last_blockchain_value(self):
        """Returns the last value of the current blockchain"""
        if len(self.__chain) < 1:
            return None
        return self.__chain[-1]

    def add_transaction(self, recipient, sender, signature, amount=1.0, is_receiving=False):
        """
        Arguments:
            :sender: The sender of the coins.
            :recipeint: The recipeint of the coins.
            :amount: The amount of coins sent with the transaction (default = 1.0)
        """
        # OrderedDict takes a list of tuples
        if self.public_Key == None:
            return False
        # above to prevent recipients that are set to None from mining blocks
        transaction = Transaction(sender, recipient, signature, amount)
        # verify transactions is valid by checking that the sender has enough coins to cover the value of the transaction
        if Verification.verify_transaction(transaction, self.get_balance):
            self.__open_transactions.append(transaction)
            self.save_data()
            # if you're creating a new transaction on this node and need to broadcast it
            if not is_receiving:
                for node in self.__peer_nodes:
                    # The url takes the port number(node) as part of the URL
                    url = "http://{}/broadcast-transaction".format(node)
                    try:
                        # try to make a request, if it fails move to the next node
                        response = requests.post(url, json={
                            "sender": sender, "recipient": recipient, "amount": amount, "signature": signature})
                        print(response)
                        if response.status_code >= 400 or response.status_code >= 500:
                            print('Transaction declined, needs resolving')
                            return False
                    except requests.exceptions.ConnectionError:
                        continue
            return True
        return False

    def mine_block(self):
        """
        Mine new blocks, add them to the block chain and reward the miner
        Thereby releasing coins into the system.
        """
        if self.public_Key == None:
            return None
        # above to prevent recipients that are set to None from mining blocks
        # in order to avoid an error if the block chain is empty, you add a genesis block to the blockchain
        last_block = self.__chain[-1]
        hashed_block = hash_block(last_block)
        proof = self.proof_of_work()
        # ordered dict so it gets save in the file and blockchain in the right order
        # Mining transaction doesn't need to be signed because it's how coins are released into the system and there's a check
        # against manipulating the amount of coins that are released
        reward_transaction = Transaction(
            "MINNING", self.public_Key, '', MINING_REWARD)
        copied_transactions = self.__open_transactions[:]
        for tx in copied_transactions:
            if not Wallet.verify_transaction(tx):
                print("The result of failed verified transactions",
                      Wallet.verify_transaction(tx))
                copied_transactions.remove(tx)
                return None
        # the code below comes after the one above because we don't want to verify Mining transactions and also don't want to introduce a
        # vulnerability in the blockchain in which we automatically set verification for Mining transactions to "True" without verifying and a blockchain attacker could
        # go into the open transactions in the blockchain file and edit other senders to "Mining" and other transactions to Mining transactions.
        copied_transactions.append(reward_transaction)
        block = Block(len(self.__chain), hashed_block,
                      copied_transactions, proof)
        self.__chain.append(block)
        self.__open_transactions = []
        self.save_data()
        for node in self.__peer_nodes:
            url = 'http://{}/broadcast-block'.format(node)
            converted_block = block.__dict__.copy()
            converted_block['transactions'] = [
                tx.__dict__ for tx in converted_block['transactions']]
            try:
                response = requests.post(url, json={'block': converted_block})
                print(response.status_code)
                if response.status_code == 400 or response.status_code == 500:
                    print('Block declined, needs resolving')
                if response.status_code == 409:
                    self.resolve_conflict = True
            except requests.exceptions.ConnectionError:
                continue
        return block  # return the mined block

    def add_block(self, block):
        """Add a block which was received via broadcasting to the local blockchain."""
        # Create a list of transaction objects
        transactions = [Transaction(
            tx['sender'], tx['recipient'], tx['signature'], tx['amount']) for tx in block['transactions']]
        # Validate the proof of work of the block and store the result (True or False) in a variable
        proof_is_valid = Verification.valid_proof(
            transactions[:-1], block['previous_hash'], block['proof'])
        # Check if previous_hash stored in the block is equal to the local blockchain's last block's hash and store the result in a block
        hashes_match = hash_block(self.chain[-1]) == block['previous_hash']
        if not proof_is_valid or not hashes_match:
            return False
        # Create a Block object
        converted_block = Block(
            block['index'], block['previous_hash'], transactions, block['proof'], block['timestamp'])
        self.__chain.append(converted_block)
        stored_transactions = self.__open_transactions[:]
        # Check which open transactions were included in the received block and remove them
        # This could be improved by giving each transaction an ID that would uniquely identify it
        for itx in block['transactions']:
            for opentx in stored_transactions:
                if opentx.sender == itx['sender'] and opentx.recipient == itx['recipient'] and opentx.amount == itx['amount'] and opentx.signature == itx['signature']:
                    try:
                        self.__open_transactions.remove(opentx)
                    except ValueError:
                        print('Item was already removed')
        self.save_data()
        return True

    def resolve(self):
        """Checks all peer nodes' blockchains and replaces the local one with longer valid ones."""
        # Below: winner chain to hold the value of the chain we'd use
        winner_chain = self.chain
        # Below: replace varaible to keep track of whether the winner_chain variable changed
        replace = False
        for node in self.__peer_nodes:
            url = f"http://{node}/chain"
            try:
                response = requests.get(url)
                node_chain = response.json()
                node_chain = [Block(block['index'], block['previous_hash'], [Transaction(
                    tx['sender'], tx['recipient'], tx['signature'], tx['amount']) for tx in block['transactions']],
                                    block['proof'], block['timestamp']) for block in node_chain]
                node_chain_length = len(node_chain)
                print(node_chain_length)
                print(Verification.verify_chain(node_chain))
                local_chain_length = len(winner_chain)
                if node_chain_length > local_chain_length and Verification.verify_chain(node_chain):
                    winner_chain = node_chain
                    replace = True
            except requests.exceptions.ConnectionError:
                continue
        self.resolve_conflict = False
        self.chain = winner_chain
        if replace:
            self.__open_transactions = []
        self.save_data()
        return replace

    def add_peer_node(self, node):
        """
            Adds a new node to the peer node set.

            Arguments:
                :node: The node URL which should be added.
        """
        self.__peer_nodes.add(node)
        self.save_data()

    def remove_peer_node(self, node):
        """
            Removes a node from the peer node set

            Arguments:
                :node: The node URL which should be removed.
        """
        self.__peer_nodes.discard(
            node)  # tries to remove the node, but doesn't throw an error if the node doesn't exist
        self.save_data()

    def get_peer_nodes(self):
        """get a list of all connected nodes"""
        return list(self.__peer_nodes)

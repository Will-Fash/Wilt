
> # An Ongoing BlockChain Program in Python.
>
>> All the core features of a blockchain are implemented. 

>#### Features Implemented are:
>
>- A wallet using Cryptographic public key systems.
>- Transaction verification and block chaining using sha256 hashing and the pkcs1_15 scheme.
>- Minning new blocks with a resulting Minning reward.
>- Chain verification
>- Storing chain to Disk in a file.
>- A Node Network using Flask
>- Sharing blocks and transactions by broadcasting
>- A consensus algorithm to resolve conflicts
>- Error Handling
>- A proof of Work with a mining diffculty set by making sure the first 2 elements of the generated hashes are zero.
> 


>#### Features to Implement:
>
>- Improve error handling
>- Improve scalability and broadcasting by making use of async programming.
>- Control minning difficulty (Dynamically)
>- Add a merkle tree for transaction verififcation
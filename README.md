### EVM Storage verifier on Starknet

Storage verifier allows to trustlessly prove a past or current storage values of L1 contracts to other L2 contracts.
In the near future also proving other things will be possible, things like:

- Specific transaction was included in the block
- A transaction consumed a given amount of gas
- Some logs where emitted during a transaction execution
- Some specific miner mined an uncle block

### Architecure

The storage verifier is built out of the following components:

- L1 messaging contracts
- L2 contract receiving L1 messages
- L2 contract storing and processing L1 block headers
- Facts registry which stores the proven facts

Flow diagram attached below:
![alt text](https://github.com/marcellobardus/starknet-l2-storage-verifier/blob/master/.github/storage-verifier.png?raw=true)

### SETUP

1. Make sure you're running a venv with python 3.7.12
   To create such a virtualenv first make sure to have `pyenv` installed.
   Then run the following commands:

- `pyenv install 3.7.12`
- `pyenv local 3.7.12`
- `virtualenv venv --python=$(which python3<x86>)`
- `source venv/bin/activate`

NOTE: If you're using apple M1 please make sure you installed python3.7 with brew arch x86 using rosetta.

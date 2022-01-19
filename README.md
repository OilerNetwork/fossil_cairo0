# Starknet Storage Verifier by Oiler Network

The Starknet Storage Verifier will allow anyone to trustlessly prove any past or current storage values of L1 contracts to other L2 contracts.

*The Storage Verifier is being developed by [Oiler Network](https://oiler.network), and will soon power many of Oiler's Derivative Products.*

## Architecure

The storage verifier is built out of the following components:

- L1 messaging contracts
- L2 contract receiving L1 messages
- L2 contract storing and processing L1 block headers
- Facts registry which stores the proven facts

![alt text](https://github.com/marcellobardus/starknet-l2-storage-verifier/blob/master/.github/storage-verifier.png?raw=true)
*Storage Verifier Flow diagram*

## Testing

In order to run the tests, please make sure to have a python 3.7 virtual environment.

## Contribute

There are countless usecases for the storage verifier and we are excited to hear what the community wants to build with it! Please reach out to <kacper@oiler.network> for any partnership, sponsorship, or other matters.

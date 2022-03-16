# Fossil - Starknet-based State Verifier by Oiler

Fossil will allow anyone to trustlessly prove any past or current headers, state, and storage values of L1 contracts to other L2 contracts.

*Fossil is being developed by [Oiler Network](https://oiler.network), and will soon power many of Oiler's Derivative Products.*

## Architecure

Fossil is built out of the following components:

- L1 messaging contracts
- L2 contract receiving L1 messages
- L2 contract storing and processing L1 block headers
- Facts registry which stores the proven facts

![alt text](https://github.com/marcellobardus/starknet-l2-storage-verifier/blob/master/.github/storage-verifier.png?raw=true)
*Storage Verifier Flow diagram*

## Testing

In order to run the tests, please make sure to have a python 3.7 virtual environment.

## Fossil API

Oiler has built an API which allows projects to take advantage of Fossil in a much simpler manner. Unfortunately, Fossil is currently not ready for most production applications. This is because the block step limit on Starknet is too low and large requests may fail if they require too many steps. We are in contact with Starkware and are awaiting for them to increase the step limit in the near future, at which time we will complete e2e testing and officially launch Fossil. If you are interested in building with the Fossil API, we can give you API access for testing purposes prior to the official launch. Please send any inquiries to: <fossil@oiler.network>

## Contribute

There are countless usecases for the storage verifier and we are excited to hear what the community wants to build with it! Please reach out to <kacper@oiler.network> for any partnership, sponsorship, or other matters.

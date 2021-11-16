from starkware.starknet.testing.contract import StarknetContract
from starkware.starknet.compiler.compile import compile_starknet_files


async def deploy(state, path, constructor_calldata):
    contract_definition = compile_starknet_files([path], debug_info=True)
    return await state.deploy(
        path,
        constructor_calldata=constructor_calldata
    )
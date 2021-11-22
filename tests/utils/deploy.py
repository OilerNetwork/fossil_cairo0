from starkware.starknet.testing.contract import StarknetContract
from starkware.starknet.compiler.compile import compile_starknet_files


async def deploy(state, path, constructor_calldata):
    compile_starknet_files([path], debug_info=True)
    deployment: StarknetContract = await state.deploy(
        path,
        constructor_calldata=constructor_calldata
    )
    return deployment
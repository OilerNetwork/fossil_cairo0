from typing import NamedTuple
import pytest
from starkware.starknet.testing.contract import StarknetContract
from starkware.starknet.testing.starknet import Starknet

class TestsDeps(NamedTuple):
    starknet: Starknet
    concat: StarknetContract

async def setup():
    starknet = await Starknet.empty()
    concat = await starknet.deploy("contracts/starknet/test/TestConcatArr.cairo", cairo_path=["contracts"])
    return TestsDeps(starknet=starknet, concat=concat)

@pytest.mark.asyncio
async def test_concat_arr():
    starknet, concat = await setup()

    acc = [10, 30, 50]
    arr = [70, 90, 110]

    concat_arr_call = await concat.test_concat_arr(acc, arr).call()
    arr_concat = concat_arr_call.result.res
    assert arr_concat == acc + arr



from typing import NamedTuple
import pytest
from starkware.starknet.testing.contract import StarknetContract
from starkware.starknet.testing.starknet import Starknet

class TestsDeps(NamedTuple):
    starknet: Starknet
    comp: StarknetContract

async def setup():
    starknet = await Starknet.empty()
    comp = await starknet.deploy("contracts/starknet/test/TestCompArr.cairo", cairo_path=["contracts"])
    return TestsDeps(starknet=starknet, comp=comp)

@pytest.mark.asyncio
async def test_comp_arr_not_eq():
    starknet, comp = await setup()

    a = [10, 30, 50]
    b = [70, 90, 110]

    concat_arr_call = await comp.test_comp_arr(a, b).call()
    res = concat_arr_call.result.res
    assert res == 0

@pytest.mark.asyncio
async def test_comp_arr_eq():
    starknet, comp = await setup()

    a = [10, 30, 50]
    b = [10, 30, 50]

    concat_arr_call = await comp.test_comp_arr(a, b).call()
    res = concat_arr_call.result.res
    assert res == 1

@pytest.mark.asyncio
async def test_comp_arr_empty():
    starknet, comp = await setup()

    a = []
    b = []

    concat_arr_call = await comp.test_comp_arr(a, b).call()
    res = concat_arr_call.result.res
    assert res == 1

@pytest.mark.asyncio
async def test_comp_arr_different_size():
    starknet, comp = await setup()

    a = []
    b = [10,20,30]

    concat_arr_call = await comp.test_comp_arr(a, b).call()
    res = concat_arr_call.result.res
    assert res == 0
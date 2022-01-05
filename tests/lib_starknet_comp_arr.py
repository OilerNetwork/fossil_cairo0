import pytest
import asyncio
from typing import NamedTuple
from starkware.starknet.testing.contract import StarknetContract
from starkware.starknet.testing.starknet import Starknet

class TestsDeps(NamedTuple):
    starknet: Starknet
    comp: StarknetContract

@pytest.fixture(scope='module')
def event_loop():
    return asyncio.new_event_loop()

async def setup():
    starknet = await Starknet.empty()
    comp = await starknet.deploy("contracts/starknet/test/TestCompArr.cairo", cairo_path=["contracts"])
    return TestsDeps(starknet=starknet, comp=comp)

@pytest.fixture(scope='module')
async def factory():
    return await setup()

@pytest.mark.asyncio
async def test_comp_arr_not_eq(factory):
    starknet, comp = factory

    a = [10, 30, 50]
    b = [70, 90, 110]

    concat_arr_call = await comp.test_comp_arr(a, b).call()
    res = concat_arr_call.result.res
    assert res == 0

@pytest.mark.asyncio
async def test_comp_arr_eq(factory):
    starknet, comp = factory

    a = [10, 30, 50]
    b = [10, 30, 50]

    concat_arr_call = await comp.test_comp_arr(a, b).call()
    res = concat_arr_call.result.res
    assert res == 1

@pytest.mark.asyncio
async def test_comp_arr_empty(factory):
    starknet, comp = factory

    a = []
    b = []

    concat_arr_call = await comp.test_comp_arr(a, b).call()
    res = concat_arr_call.result.res
    assert res == 1

@pytest.mark.asyncio
async def test_comp_arr_different_size(factory):
    starknet, comp = factory

    a = []
    b = [10,20,30]

    concat_arr_call = await comp.test_comp_arr(a, b).call()
    res = concat_arr_call.result.res
    assert res == 0
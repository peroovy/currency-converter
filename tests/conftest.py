from asyncio import AbstractEventLoop, get_event_loop_policy

import pytest


@pytest.fixture(scope="session")
def event_loop() -> AbstractEventLoop:
    policy = get_event_loop_policy()
    loop = policy.new_event_loop()

    yield loop

    loop.close()

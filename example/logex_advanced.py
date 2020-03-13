import asyncio
import concurrent.futures
import time
import structlog
from logma.wech import datlog

datlog()
log = structlog.get_logger("logex_advanced")


def slooow_func(num):
    log.info('calc', num=num)
    time.sleep(0.1)
    log.info('finished', num=num)
    return num * num


async def run_slow_tasks(executor):
    loop = asyncio.get_event_loop()
    slow_tasks = [
        loop.run_in_executor(executor, slooow_func, i)
        for i in range(4)
    ]
    log.info('await slow_tasks')
    completed, pending = await asyncio.wait(slow_tasks)
    results = [t.result() for t in completed]
    log.info(f'results: {results}')


if __name__ == '__main__':
    log.info("Advanced example with threads, processes and asyncio")
    # Create a limited thread pool.
    texecutor = concurrent.futures.ThreadPoolExecutor(
        max_workers=3,
        thread_name_prefix="Thread"
    )
    pexecutor = concurrent.futures.ProcessPoolExecutor(
        max_workers=3,
        # thread_name_prefix="Thread"
    )

    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(
        run_slow_tasks(texecutor)
    )
    event_loop.run_until_complete(
        run_slow_tasks(pexecutor)
    )
    event_loop.close()

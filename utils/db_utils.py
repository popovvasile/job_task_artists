from functools import wraps

from sessions.session import LocalSession


class Transactional:
    def __call__(self, func):
        @wraps(func)
        async def _transactional(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                await LocalSession.commit()
            except Exception as e:
                await LocalSession.rollback()
                raise e

            return result

        return _transactional

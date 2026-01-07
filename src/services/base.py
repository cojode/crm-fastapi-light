from src.logger import logger


class UseCaseMeta(type):
    USE_CASE_DEBUG_PREFIX = "[USE CASE]"

    def __new__(cls, name, bases, namespace):
        if "execute" in namespace:
            original_execute = namespace["execute"]

            async def wrapped_execute(self, *args, **kwargs):
                logger.info(
                    "%s Entering %s.execute with args: %s, kwargs: %s",
                    cls.USE_CASE_DEBUG_PREFIX,
                    name,
                    args,
                    kwargs,
                )
                try:
                    result = await original_execute(self, *args, **kwargs)
                    logger.info(
                        "%s %s.execute completed with result: %s",
                        cls.USE_CASE_DEBUG_PREFIX,
                        name,
                        result,
                    )
                    return result
                except Exception as e:
                    logger.info(
                        "%s %s.execute failed with error: %s",
                        cls.USE_CASE_DEBUG_PREFIX,
                        name,
                        str(e),
                    )
                    raise

            namespace["execute"] = wrapped_execute
        return super().__new__(cls, name, bases, namespace)


class BaseUseCase(metaclass=UseCaseMeta): ...

import structlog

logger = structlog.get_logger()


def call():
    logger.info("This info call")
    logger.debug("This hidden debug call")
    logger.info("This is another info call")

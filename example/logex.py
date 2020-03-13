from logma.wech import datlog
import structlog


# auto detects tty and outputs json or text accordingly
datlog()


log = structlog.get_logger("logex")


def main():
    log.info("Hello")
    log.warn("Hello")
    log.error("Hello")
    log.debug("Hello")


if __name__ == "__main__":
    main()

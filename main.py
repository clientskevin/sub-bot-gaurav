import sys

from loguru import logger

from app import Bot, configs

if __name__ == "__main__":
    # Configure logger
    logger.remove()
    logger.add(
        sys.stderr,
        level=configs.LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    )

    logger.info("Application is starting...")
    bot = Bot()

    try:
        bot.run()
    except KeyboardInterrupt:
        logger.warning("Application interrupted by user.")
    except Exception as e:
        logger.exception(f"Application crashed: {e}")
    finally:
        logger.info("Application shutdown complete.")

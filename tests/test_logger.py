import logging

from src import logger as logger_module


def _cleanup_logger(logger: logging.Logger) -> None:
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()


def test_get_logger_creates_logger():
    logger = logger_module.get_logger("test_logger_creation")

    try:
        assert logger.name == "test_logger_creation"
        assert logger.propagate is False
        assert logger.handlers
    finally:
        _cleanup_logger(logger)


def test_get_logger_creates_log_file_when_configured(tmp_path, monkeypatch):
    log_file = tmp_path / "app.log"
    monkeypatch.setattr(logger_module, "DEFAULT_LOG_FILE", str(log_file))

    logger = logger_module.get_logger("test_logger_file_creation")

    try:
        logger.info("hello")
        for handler in logger.handlers:
            handler.flush()
        assert log_file.exists()
    finally:
        _cleanup_logger(logger)

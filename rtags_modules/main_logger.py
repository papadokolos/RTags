import logging


def InitializeMainLogger(main_logger):
    """Apply required settings to the main RTags logger.
    """
    if not main_logger.hasHandlers():
        # Must be set to lowest level to get total freedom in handlers
        main_logger.setLevel(logging.DEBUG)

        # Disable log duplications when reloading
        main_logger.propagate = False

        # Create / override console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)

        # Create formatter and add it to the handler
        formatter = logging.Formatter('[RTags / %(levelname)s] %(message)s')
        console_handler.setFormatter(formatter)

        # Add the handler to logger
        main_logger.addHandler(console_handler)


logger = logging.getLogger(__name__)
InitializeMainLogger(logger)

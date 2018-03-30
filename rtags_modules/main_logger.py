import sublime  # To obtain plugin settings
import logging


# Define the plugin logger, to be initialized on `plugin_loaded()`
logger = logging.getLogger(__name__)


def InitializeMainLogger():
    """ Apply required settings to the main RTags logger.
    """
    # Remove all previously added handlers, if any (relevant when reloading)
    logger.handlers = []

    # Must be set to lowest level to get total freedom in handlers
    logger.setLevel(logging.DEBUG)

    # Disable log duplications when reloading
    logger.propagate = False

    # Create console handler with the requested logging level
    console_handler = logging.StreamHandler()
    logging_level = GetRequestedLoggingLevel()
    console_handler.setLevel(logging_level)

    # Create formatter and add it to the handler
    formatter = logging.Formatter('[RTags / %(levelname)s] %(message)s')
    console_handler.setFormatter(formatter)

    # Add the handler to logger
    logger.addHandler(console_handler)


def GetRequestedLoggingLevel():
    """ Returns the appropriate logging level value by the plugin settings.
    """
    rtags_settings = sublime.load_settings("RTags.sublime-settings")
    verbose_logging = rtags_settings.get("verbose")
    return logging.DEBUG if verbose_logging else logging.WARNING


def ReinitializeMainLogger():
    """ Reinitializes the plugin's logger in case the settings have changed.
    """
    if logger.handlers[0].level != GetRequestedLoggingLevel():
        InitializeMainLogger()

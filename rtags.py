import sublime

# Import the plugin logger to initialize on plugin load
from RTags.rtags_modules import main_logger

# Import all RTags functionality commands
from RTags.rtags_commands.follow_location import FollowLocationCommand
from RTags.rtags_commands.find_references import FindReferencesCommand, PublishResultsToPanelCommand
from RTags.rtags_commands.find_references_virtual_methods import FindReferencesForVirtualMethodOverridesCommand


def plugin_loaded():
    # Initialize the plugin's logger
    main_logger.InitializeMainLogger()

    # Re-initialize the logger on settings change
    sublime.load_settings("RTags.sublime-settings").add_on_change(
        "reinitialize-logger", main_logger.ReinitializeMainLogger)

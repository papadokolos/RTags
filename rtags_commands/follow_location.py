import sublime_plugin

from RTags.rtags_modules.main_logger import logger
from RTags.rtags_modules.rc_call import RCCall
from RTags.rtags_modules.cursor_manipulations import CursorLocationHelper


class FollowLocationCommand(sublime_plugin.TextCommand):
    def __init__(self, *args):
        super().__init__(*args)
        # Flags that will be given to rc call, as a format
        self._rc_params_format = "--no-context --follow-location {location}"

    def run(self, edit):
        logger.info("The functional command '{}' has been triggered.".format(
            self.__class__.__name__))

        # Get current cursor location, and assure it is single
        location = CursorLocationHelper.extract_single_location(
            view=self.view, avoid_word_end=True)
        if not location:
            self.view.window().status_message(
                "RTags: Can't follow location for multiple cursors/selection.")
            return

        # Execute rc command
        rc_params = self._rc_params_format.format(location=location)
        rc_thread = RCCall()
        rc_thread.execute_rc(rc_params)
        rc_thread.join()

        if rc_thread.rc_returned_successfully:
            if not rc_thread.received_output:
                # Ignore empty output
                logger.info("rc returned with an empty output, ignoring...")
                return

            # Parse rc command output
            file_name, row, col = self._parse_output(rc_thread.received_output)

            # Navigate to the result
            CursorLocationHelper.set_cursor_location(
                self.view, file_name, row, col)
        else:
            self.view.window().status_message(
                "RTags: Failed to follow location of symbol under cursor.")
            # # Fall back to Sublime's go-to definition.
            # # It will notify the user in case of failure
            # self.view.window().run_command('goto_definition')

    def _parse_output(self, output):
        """ Parse `output` received from "rc" to a useful form.

        Assuming output format is "{target_filename}:{row}:{col}:".
        """
        logger.debug("Parsing output returned from rc call.")

        # Extract target location from output (remove trailing colon)
        target_location = output[:-1]  # "{target_location}:"

        # Split target location to target file name, row and col
        delimiter = ':'  # "{target_filename}:{row}:{col}"
        target_filename, row, col = target_location.split(delimiter)

        return target_filename, (int)(row), (int)(col)

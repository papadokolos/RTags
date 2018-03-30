import sublime
import sublime_plugin

import json  # To get symbol length out of symbol information

from RTags.rtags_modules.main_logger import logger
from RTags.rtags_modules.rc_call import RCCall
from RTags.rtags_modules.cursor_manipulations import CursorLocationHelper


class FindReferencesCommand(sublime_plugin.TextCommand):
    def __init__(self, *args):
        super().__init__(*args)
        # Flags that will be given to rc call, as a format
        self._rc_params_format = "--references {location}"
        # Whether the symbol should be higlighted in the results panel
        self._highlight_results = True

    def run(self, edit):
        logger.info("The functional command '{}' has been triggered.".format(
            self.__class__.__name__))

        # Get current cursor location, and assure it is single
        location = CursorLocationHelper.extract_single_location(
            view=self.view, avoid_word_end=True)
        if not location:
            self.view.window().status_message(
                "RTags: Cannot find references for multiple cursors.")
            return

        # Execute rc command
        rc_params = self._rc_params_format.format(location=location)
        rc_thread = RCCall(self.view.file_name())
        rc_thread.execute_rc(rc_params)
        rc_thread.join()

        if rc_thread.rc_returned_successfully:
            # Parse rc command output
            find_results, symbol_occurences, num_of_results, num_of_files = (
                self._parse_output(rc_thread.received_output))

            # Publish results to the user
            self._create_results_panel(find_results, symbol_occurences)
            self.view.window().status_message(
                "RTags: Found {} references across {} files.".format(
                    num_of_results, num_of_files))
        else:
            self.view.window().status_message(
                "RTags: Failed to find references of symbol under cursor.")

    def _parse_output(self, output):
        """ Parse `output` received from "rc" to a useful form.

        Returns:
         - String containing the results in a format matching the appropriate
           syntax definition (See `_create_results_panel()`)
         - Occurences list of the referenced symbol (row, col_start, col_end)
         - Statistics about the results (number of references, number of files)

        Assuming output is multiple lines of the format:
            "{target_filename}:{row}:{col}:{line_content}"

        The output is converted to match Sublime Text's "Find Results" syntax:
            {target_filename}:
             {row}: {line_content}
        """
        def _get_symbol_column_range(symbol_location):
            """Figure out the start and end columns of the referenced symbol.
            """
            rc_params = "--json --symbol-info {}".format(symbol_location)
            rc_thread = RCCall(self.view.file_name())
            rc_thread.execute_rc(rc_params)
            rc_thread.join()

            if not rc_thread.rc_returned_successfully:
                raise RuntimeError(
                    "Failed to get referenced symbol information")

            output_without_whitesapces = ''.join(
                rc_thread.received_output.split())
            output_as_dict = json.loads(output_without_whitesapces)

            if output_as_dict["endLine"] != output_as_dict["startLine"]:
                raise ValueError(
                    "A symbol is not supposed to spread over multiple lines.")

            return output_as_dict["startColumn"], output_as_dict["endColumn"]

        logger.debug("Parsing output returned from rc call.")

        # Will contain the result of the parse
        find_results = ''

        # Will contain statistics about the find results
        number_of_results = 0
        number_of_files = 0

        # List of (row, col_start, col_end) tuples of the referenced symbol
        # occurences. note: row and col are zero based
        symbol_occurences = []

        # Every file name should be mentioned once, so duplications are removed
        previous_target_filename = ''
        previous_row = 0
        line_number = 0
        for line in output.splitlines():
            # Split output line to target file name, row, col and context
            delimiter = ':'
            target_filename, row, col, context = line.split(
                delimiter, maxsplit=3)

            # Whether current result belongs to a different file (against prev)
            if target_filename != previous_target_filename:
                # Bind future results to current target file name
                find_results += target_filename + ':\n'

                # Append current result line
                find_results += ' ' + row + ':' + context + '\n'

                previous_row = row
                previous_target_filename = target_filename
                number_of_files += 1
                line_number += 1
            elif row != previous_row:
                # No need to print multiple results for the same line number
                # Append current result line
                find_results += ' ' + row + ':' + context + '\n'
                previous_row = row
            else:
                # Cancel line number increase from previous iteration
                line_number -= 1

            # Calculate the column offset for the referenced symbol occurence
            # The offset considers: " {row}:<tabstop>"
            offset = 1 + len(row) + 1

            if self._highlight_results:
                # Used to calculate the end column of the referenced symbol
                symbol_location = ':'.join((target_filename, row, col))
                col_start, col_end = _get_symbol_column_range(symbol_location)
                col_start += offset
                col_end += offset

                # Add the referenced symbol occurence to the list
                symbol_occurences.append((line_number, col_start, col_end))

            number_of_results += 1
            line_number += 1

        return (
            find_results,
            symbol_occurences,
            number_of_results,
            number_of_files)

    def _create_results_panel(self, find_results, symbol_occurences):
        """ Create a Find Results panel, fill it with `find_results`, and
        highlight all `symbol_occurences`.
        """
        logger.debug("Preparing results panel.")

        syntax = "Packages/RTags/Find References Results.hidden-tmLanguage"
        file_regex = '^([^ \t].*):$'
        line_regex = '^ +([0-9]+):'
        working_dir = ''
        results_panel_name = "RTags - References"

        results_view = self.view.window().create_output_panel(
            results_panel_name)
        results_view.settings().set("result_file_regex", file_regex)
        results_view.settings().set("result_line_regex", line_regex)
        results_view.settings().set("result_base_dir", working_dir)
        results_view.settings().set("word_wrap", False)
        results_view.settings().set("line_numbers", False)
        results_view.settings().set("gutter", True)
        results_view.settings().set("scroll_past_end", False)
        results_view.settings().set("rulers", [])
        results_view.settings().set("translate_tabs_to_spaces", False)
        results_view.settings().set("highlight_line", True)
        results_view.settings().set("fold_buttons", True)
        results_view.settings().set("fade_fold_buttons", False)
        results_view.assign_syntax(syntax)

        results_view.run_command("publish_results_to_panel", {
            "results_panel_name": results_panel_name,
            "results": find_results,
            "symbol_occurences": symbol_occurences})


class PublishResultsToPanelCommand(sublime_plugin.TextCommand):
    """ Fill accepted view with given results, focus the view, and highlight
    all symbol occurences.
    """

    def run(self, edit, results_panel_name, results, symbol_occurences):
        logger.debug("The helper command '{}' has been triggered.".format(
            self.__class__.__name__))

        # Fill the view with the results
        self.view.insert(edit, 0, results)

        # Assure results navigation (if configured) starts from the beggining
        self.view.sel().clear()

        # In case there are occurences which we would like to highlight
        if symbol_occurences:
            # Convert symbol occurences to regions
            regions_to_highlight = [
                sublime.Region(
                    self.view.text_point(row, col_start),
                    self.view.text_point(row, col_end))
                for row, col_start, col_end in symbol_occurences]

            # Highlight all symbol occurences
            flags = (
                sublime.DRAW_STIPPLED_UNDERLINE |
                sublime.DRAW_NO_FILL |
                sublime.DRAW_NO_OUTLINE)

            self.view.add_regions(
                "symbol",
                regions_to_highlight,
                scope="storage.type",
                flags=flags)

        # Present the results panel to the user
        sublime.active_window().run_command(
            "show_panel", {"panel": "output." + results_panel_name})
        sublime.active_window().focus_view(self.view)

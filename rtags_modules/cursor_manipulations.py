"""
Contains helper methods for cursor manipulations.

What is a cursor?
    A cursor is the blinking line representing your current write position.
    Sublime Text supports multiple cursors. Meaning that you can write at
    multiple locations at the same time (in the same view).
"""

import sublime

from Default import history_list  # Manages Sublime's cursor location history
import os.path  # For extracting symbolic links when comparing paths

from RTags.rtags_modules.main_logger import logger


class CursorLocationHelper(object):
    """ Helps getting, converting and modifying cursors locations.
    """

    @staticmethod
    def extract_single_location(view, avoid_word_end=False):
        """ Return a single cursor's absolute location ({file}:{row}:{col})

            Extract the location of the cursor from a "view" object in format
            {file}:{row}:{col}. In case `view` contains more than a single
            location, empty string ("") is returned.

            In case `avoid_word_end`=True, identify the word in which the
            cursor is in, and if the cursor is at the end of that word, return
            the location of the beginning of it. This option is useful in case
            the location is to be used in a call for rc, since it has a bug
            when handling such locations.
        """

        # Assure there is only a single cursor
        if CursorLocationHelper._is_single_cursor(view):
            logger.debug(
                "Can't extract single location from multiple cursors.")
            return ""

        # Assure that cursor (which represented by region) is not a selection
        region = view.sel()[0]
        if CursorLocationHelper._is_selection(region):
            logger.debug(
                "Can't extract single location from non-empty selection.")
            return ""

        # Extract cursor's point from the cursor's region
        point = region.a

        if avoid_word_end:
            if CursorLocationHelper._is_end_of_word(view, point):
                # Reassign point to the beggining of the word
                point = view.find_by_class(
                    pt=point,
                    forward=False,
                    # Support operator overloading (words of only punctuations)
                    classes=sublime.CLASS_WORD_START |
                    sublime.CLASS_PUNCTUATION_START)

        # Convert current cursor location from "point" to "row" and "col"
        zero_based_row, zero_based_col = view.rowcol(point)
        row, col = zero_based_row + 1, zero_based_col + 1

        return CursorLocationHelper._to_absolute_location(
            view.file_name(), row, col)

    @staticmethod
    def set_cursor_location(source_view, dest_file_name, dest_row, dest_col):
        """ Move `source_view`'s cursor/s location to a new destination.

        Params:
            source_view    - sublime.view instance to modify its cursor
            dest_file_name - destination file name (absolute path)
            dest_row       - destination row number (nonzero based)
            dest_col       - destination column number (nonzero based)

        Note:
            - This method affects sublime's cursor locations history.
            - `source_view`'s cursors will be modified only in case the
            destination cursor location is in the same view.
        """
        logger.debug("About to navigate to a new location.")

        # New cursor location is in the source view
        if os.path.realpath(source_view.file_name()) == dest_file_name:
            CursorLocationHelper._set_cursor_location_same_view(
                source_view, dest_row, dest_col)

        # New cursor location is in a different view
        else:
            try:
                # Fix project/folder path prefix within absolute path, in case
                # the directed file is actually a part of it.
                dest_file_name = (CursorLocationHelper._to_project_path(
                    dest_file_name))
                logger.debug("New location is within the project path.")
            except CursorLocationHelper.FileOutsideProjectPathError:
                # No modification should be done in this case
                logger.debug("New location is outside the project path.")
                pass

            CursorLocationHelper._set_cursor_location_different_view(
                source_view, dest_file_name, dest_row, dest_col)

    @staticmethod
    def _is_single_cursor(view):
        """ Return whether multiple cursors are in use, or just one.
        """
        return len(view.sel()) != 1

    @staticmethod
    def _is_selection(region):
        """ Return whether `region` represents an empty selection, or not.
        """
        return not region.empty()

    @staticmethod
    def _is_end_of_word(view, point_in_view):
        """ Return whether `point_in_view` directs to an ending of word, or not.
        """
        return view.classify(point_in_view) & sublime.CLASS_WORD_END

    @staticmethod
    def _to_absolute_location(file, row, col):
        """ Convert `file`, `row` and `col` strings to a string of the format
            {file}:{row}:{col}.
        """
        return "{}:{}:{}".format(file, row, col)

    @staticmethod
    def _to_project_path(absolute_path):
        """ Modify `absolute_path` such that it will be prefixed correctly with
            the current project/folder root directory, in case it is inside it.

            An actual modification only takes place if current project/folder
            root directory path contains symbolic links. Exception is raised in
            case `absolute_path` directs to a file outside of the
            project/folder.

            Note:
                This method is capable of handling projects with multiple root
                directories, and also directories that were opened directly
                without regard to Sublime's Project feature.

            Motivation:
                SublimeText treats files opened via paths containing symbolic
                links as different from one another, and I wanted to avoid it.
                Refer to https://github.com/SublimeTextIssues/Core/issues/611
                for more information.

            Credits:
                Many thanks to `Path Tools` plugin for the main logic
        """
        project_root_directories = (
            directory for directory in sublime.active_window().folders())

        for project_root_dir in project_root_directories:
            # Root directories might contain symlinks that must be extracted
            project_root_dir_extracted = os.path.realpath(project_root_dir)
            if absolute_path.startswith(project_root_dir_extracted):
                return project_root_dir + absolute_path[
                    len(project_root_dir_extracted):]

        raise CursorLocationHelper.FileOutsideProjectPathError(
            "The given path does not point to a file within the current"
            "project/folder: \"{}\"".format(absolute_path))

    @staticmethod
    def _set_cursor_location_same_view(source_view, dest_row, dest_col):
        """ Set `source_view`'s cursor/s to a new location at the same view.
        """
        logger.debug("Navigating to location within the same view.")

        # Save last cursor location for future use of 'jump_back' command
        cursor_locations_history = history_list.get_jump_history(
            source_view.window().id())
        cursor_locations_history.push_selection(source_view)

        # Modify the view's selection (cursors) by clearing and setting new one
        sel = source_view.sel()
        sel.clear()

        zero_based_row, zero_based_col = dest_row - 1, dest_col - 1
        point = source_view.text_point(zero_based_row, zero_based_col)
        sel.add(point)
        source_view.show(point)

    @staticmethod
    def _set_cursor_location_different_view(
            source_view, dest_file_name, dest_row, dest_col):
        """ Navigate to a different view directly to the desired position.
        """
        logger.debug("Navigating to location within a different view.")

        target_location = ':'.join(
            [dest_file_name, str(dest_row), str(dest_col)])

        # Last cursor location is automatically saved for future use of
        # 'jump_back' command.
        source_view.window().open_file(
            target_location,
            sublime.ENCODED_POSITION)

    class FileOutsideProjectPathError(ValueError):
        """ Value does not point to a file within the current project/folder.
        """
        pass

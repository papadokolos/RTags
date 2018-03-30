import sublime
import sublime_plugin

from RTags.rtags_modules.main_logger import logger
from RTags.rtags_modules.rc_call import RCCall

import os


class LoadCompileCommandsCommand(sublime_plugin.WindowCommand):
    def run(self):
        logger.info("The functional command '{}' has been triggered.".format(
            self.__class__.__name__))

        # Find all "compile_commands.json" files located in open folders
        compile_commands_file_path_results = [
            os.path.join(folder, file)
            for folder in self.window.folders()
            for file in os.listdir(folder)
            if file == "compile_commands.json"]

        logger.debug("Found compile_commands.json files at:\n  {}".format(
            compile_commands_file_path_results))

        if not compile_commands_file_path_results:
            sublime.error_message(
                "[RTags error]\n\n" +
                "There is no compile_commands.json in your environment.")
            return

        if len(compile_commands_file_path_results) > 1:
            sublime.error_message(
                "[RTags error]\n\n" +
                "Multiple compile_commands.json files found in environment.\n"
                "I don't know which one to load, so I'll leave it to you.")
            return

        # Execute rc command
        compile_commands_path = compile_commands_file_path_results[0]
        rc_params = "--load-compile-commands {}".format(compile_commands_path)
        rc_thread = RCCall()
        rc_thread.execute_rc(rc_params)
        rc_thread.join()

        if rc_thread.rc_returned_successfully:
            self.window.status_message(
                "RTags: The compilation database was loaded successfully.")
        else:
            sublime.error_message(
                "[RTags error]\n\n" +
                "RC failed to load the compilation database.\n"
                "RTags can't work without it.\n"
                "Please refer to @StavE.")

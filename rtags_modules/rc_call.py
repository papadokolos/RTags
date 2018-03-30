"""
Provides easy and generic execution for rc commands.
"""

import sublime

import subprocess  # Used for executing "rc" command
import threading   # Enables execution of "rc" command in a separete thread

from RTags.rtags_modules.main_logger import logger


class RCCall(threading.Thread):
    """ Represents a call for "rc" command.
    """

    """ Class Constants """
    # RTags protocol version number supported by this plugin
    _PROTOCOL_VERSION = 124

    # Amount of second given to rc call to complete its communication with rdm
    _TIMEOUT = 10

    def __init__(self, view_file_path=None):
        """ Create an RCCall instance, and initialize its members

            Params:
                view_file_path - Full file path of the currently active view
        """
        super(RCCall, self).__init__()

        """ Public members """
        self.view_file_path = view_file_path
        self.rc_returned_successfully = False
        self.received_output = ""

        """ Private members """
        # Default parameters to be used in any rc call
        self._rc_default_params = [
            "--no-color",
            "--absolute-path",
            "--verify-version={}".format(self._PROTOCOL_VERSION)]

        if view_file_path:
            self._rc_default_params.append("--current-file={}".format(
                self.view_file_path))

        # User defined parameters to be used in any rc call
        self._rc_user_params = []

    def run(self):
        # Clear result of previous rc call
        self.received_output = ""
        self.rc_returned_successfully = False

        command = self._build_command()
        logger.debug("About to execute rc command: \"{}\"".format(command))

        # Try to execute rc command, and handle the result
        try:
            binary_output = subprocess.check_output(
                command.split(), timeout=self._TIMEOUT, shell=False)
        except subprocess.CalledProcessError as e:
            self._log_rc_error(command, e)
        except subprocess.TimeoutExpired as e:
            self._log_rdm_timeout_error(command, e)
        else:
            str_output = binary_output.decode('UTF-8').strip()
            self._log_rc_success(str_output)
            self.received_output = str_output
            self.rc_returned_successfully = True

    def execute_rc(self, *rc_user_params):
        """ Execute "rc" command with given parameters on a separate thread.
        """
        self._set_params(*rc_user_params)
        self.start()

    def _set_params(self, *rc_user_params):
        """ Assign parameters for next "rc" execution.
        """
        self._rc_user_params = list(rc_user_params)

    def _build_command(self):
        """ Combine default and user parameters to create a valid "rc" command
        """
        return "rc {}".format(
            ' '.join(
                self._rc_default_params + self._rc_user_params))

    @staticmethod
    def _log_rc_success(output):
        """ Log about a successful execution of an rc command.

        Params:
            output - UTF-8 decoded output of that command
        """
        success_msg_format = "Successfully executed rc command:\n \"{}\""
        success_msg = success_msg_format.format(output)
        logger.debug(success_msg)

    @staticmethod
    def _log_rc_error(cmd, e):
        """ Log about an error in rc execution.

        Params:
            cmd - rc command that caused the error
            e   - CalledProcessError exception

        RC exit codes:
            success - 0
            general_failure - 32
            network_failure - 33
            timeout_failure - 34
            not_indexed - 35
            connection_failure - 36
            protocol_failure - 37
            argument_parse_error - 38
        """
        # Errors that should be supressed from the normal user
        rc_exit_codes_unrelevant_to_user = {
            "general_failure": 32,
            "network_failure": 33,
            "timeout_failure": 34,
            "argument_parse_error": 38
        }

        # Errors that the user must be notified about
        rc_exit_codes_very_relevant_to_user = {
            "not_indexed": {
                "exit_code": 35,
                "user_friendly_message":
                "The current file is not indexed within rdm server.\n\n"
                "Possible reasons are:\n"
                "- Missing compile_commands.json file\n"
                "- Outdated compile_commands.json file\n"
                "- Rdm sever is not watching this compile_commands.json\n"
            },
            "connection_failure": {
                "exit_code": 36,
                "user_friendly_message":
                "Failed to connect to rdm server.\n"
                "Are you sure it is running?"
            },
            "protocol_failure": {
                "exit_code": 37,
                "user_friendly_message":
                "Protocol version mismatch.                                 \n"
                "This plugin version does not support your RTags installation "
                "version."
            },
        }

        error_msg_format = (
            "Executing rc resulted in an error (return code {}).\n"
            " Command: \"{}\"\n"
            " Output: \"{}\"")
        error_msg = error_msg_format.format(
            e.returncode, cmd, e.output.decode('UTF-8').strip())

        # Classify the exit code by how relevant it is for the user
        if e.returncode not in rc_exit_codes_unrelevant_to_user.values():
            for very_relevant_error in (
                    rc_exit_codes_very_relevant_to_user.values()):
                if e.returncode == very_relevant_error["exit_code"]:
                    sublime.error_message(
                        "[RTags error]\n\n" +
                        very_relevant_error["user_friendly_message"])
                    break
            logger.error(error_msg)
        else:
            error_msg = "RC error supressed from user:\n" + error_msg
            logger.debug(error_msg)

    @staticmethod
    def _log_rdm_timeout_error(cmd, e):
        """ Log about rdm taking too long to fully respond to a rc request.

        Params:
            cmd - rc command that caused the error
            e   - TimeoutExpired exception
        """
        error_msg_format = (
            "Executing rc took too long, timeout expired ({} seconds).\n"
            " Command: \"{}\"\n"
            " Output: \"{}\"")
        error_msg = error_msg_format.format(
            e.timeout, cmd, e.output.decode('UTF-8').strip())
        logger.error(error_msg)

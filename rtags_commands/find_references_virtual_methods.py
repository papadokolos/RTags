from RTags.rtags_commands.find_references import FindReferencesCommand


class FindReferencesForVirtualMethodOverridesCommand(FindReferencesCommand):
    def __init__(self, *args):
        super().__init__(*args)
        # Flags that will be given to rc call, as a format
        self._rc_params_format += " --find-virtuals"
        self._highlight_results = False

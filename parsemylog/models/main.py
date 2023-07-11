from pathlib import Path
import core.global_var as globalvar

from .log_format_parser import LogFormatParser

class Model():
    def __init__(self) -> None:
        self.log = globalvar.get_val("LOGGER")
        self.log_format_parser = LogFormatParser()

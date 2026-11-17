import warnings


# -------------------------------------------------------
# custom error and warnings classes to display custom
# messages
# ------------------------------------------------------


class Md2miscError(Exception):
    """
    base class for all errors of md2misc. `message` holds the text of the error.
    """
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return self.message


class Md2miscWarning(UserWarning):
    """
    the category of the warnings of md2misc. a caller can filter these warnings, or make them errors,
    with the `warnings` module.
    """


class UnsupportedConstruct(Md2miscError):
    """
    a Markdown construct that the output format cannot write. `line` is the line of the construct, if
    known. `describe(source)` gives the message with the name of the Markdown file.
    """
    def __init__(self, backend: str, construct: str, line: int = None):
        """
        :param backend: the name of the output format
        :param construct: the name of the Markdown construct, for example `block quote`
        :param line: the line of the construct in the Markdown text, if known
        """
        self.backend = backend
        self.construct = construct
        self.line = line
        super().__init__(self.describe())

    def describe(self, source: str = None) -> str:
        """
        the message. `source` is the name of the Markdown file, if known.
        """
        place = ""
        if source and self.line:
            place = f"{source}:{self.line}: "
        elif source:
            place = f"{source}: "
        elif self.line:
            place = f"line {self.line}: "
        return f"{place}the {self.backend} output cannot write this Markdown construct: {self.construct}"


class DocumentError(Md2miscError):
    """
    a problem with the document as a whole, or with the values that the caller gives for it.
    """


class ParsingException(Md2miscError):
    """
    base class for all parsing exceptions.
    """


class IndentationException(ParsingException):
    """
    error logs relative to list indentation
    """
    logs = {
        "firstindent": "ERROR. - inconsistant indentation in markdown list \n"
                       + "`@@TOKEN@@` \n"
                       + "all items must be as indented than the first list item or more.",
        "multiplier": "ERROR. inconsistant indentation level in list \n"
                      + "`@@TOKEN@@` \nall list items must share a common indentation multiplier.\n"
                      + "the first indented item defines the indentation multiplier."

    }  # all possible error logs

    def __init__(self, key, lstext):
        """
        :param key: the error key to select the message
        :param lstext: the text representation of the markdown list on which this error happened
        """
        super().__init__(IndentationException.logs[key].replace("@@TOKEN@@", lstext))


class Warnings:
    """
    class to give custom warnings, with the category `Md2miscWarning`. the warnings do not change the output.
    """
    logs = {
        "list_deep_nesting": "deep list nesting. you may need to change base tex options in the header.",
        "lang_not_supported": "language `@@TOKEN@@` is not supported by minted/Pygments. see https://pygments.org/languages/ for a list of supported languages.",
        "link_type_not_supported": "type of link `@@TOKEN@@` is not supported. leaving as is...",
    }

    def __init__(self, key, val=None):
        """
        give a warning to the caller.
        :param key: the key pointing to the message from Warnings.log to print
        :param val: a possible value for a custom warning message.
        """
        warnings.warn(Warnings.logs[key].replace("@@TOKEN@@", val or ""), Md2miscWarning, stacklevel=3)

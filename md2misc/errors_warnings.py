import click


# -------------------------------------------------------
# custom error and warnings classes to display custom
# messages
# ------------------------------------------------------


class UnsupportedConstruct(click.ClickException):
    """
    a Markdown construct that the output format cannot write. the command line
    tool shows the message and exits with a non-zero status.
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


class DocumentError(click.ClickException):
    """
    a problem with the document as a whole, or with the values that the caller gives for it.
    the command line tool shows the message and exits with a non-zero status.
    """


class ParsingException(click.ClickException):
    """
    base class for all parsing exceptions. the command line tool shows the message and exits with a
    non-zero status.
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


class InputException(click.ClickException):
    """
    base class for all errors caused by user input: files not found, invalid files...
    the command line tool shows the message and exits with a non-zero status.
    """
    logs = {
        "not_md": "ERROR - filename `@@TOKEN@@` doesn't end with `.md` "
                  + "and doesn't seem to be a markdown file. exiting...",
        "not_inpath": "ERROR - input file `@@TOKEN@@` not found. exiting...",
        "not_template": "ERROR - custom tex template `@@TOKEN@@` not found. exiting...",
        "template_no_token": "ERROR - custom tex template `@@TOKEN@@` does not contain a "
                        + "@@BODYTOKEN@@ key. cannot perform replacement.",
        "not_outpath": "ERROR - output directory or directories for path `@@TOKEN@@` don't "
                       + "seem to exist. create it and start again...",
        "outpath_slashes": "ERROR - output file path `@@TOKEN@@` contains '/' and '\\'. "
                           + "please remove slashes or backslashes to continue."
                           + "exiting...",
        "document_class": "ERROR - invalid value provided for argument `--document-class`: `@@TOKEN@@`. "
                          + "allowed values are `article` or `book`. exiting..."
    }  # all possible error logs

    def __init__(self, key, val=None):
        """
        :param key: the error key to select the message
        :param val: the user inputted value which caused the error
        """
        super().__init__(InputException.logs[key].replace("@@TOKEN@@", val))


class Warnings:
    """
    class to display custom warning errors. the warnings go to standard error, thus they are not
    part of the output that `--stdout` writes.
    """
    logs = {
        "outpath_extension": "WARNING - file extension of output file `@@TOKEN@@` changed to `.tex`",
        "list_deep_nesting": "WARNING - deep list nesting. you may need to change base tex options in the header.",
        "lang_not_supported": "WARNING - language `@@TOKEN@@` is not supported by minted/Pygments. see https://pygments.org/languages/ for a list of supported languages.",
        "link_type_not_supported": "WARNING - type of link `@@TOKEN@@` is not supported. leaving as is...",
    }

    def __init__(self, key, val=None):
        """
        display a warning message to the user.
        :param key: the key pointing to the message from Warnings.log to print
        :param val: a possible value for a custom warning message.
        """
        click.echo(Warnings.logs[key].replace("@@TOKEN@@", val), err=True)

"""
the regular expressions of the Markdown constructs, and the tokens of the conversion.

the converters and the source check of a backend use these expressions, so that they find the same constructs.
"""

# simple constructs
BOLD = r"(?<!\*)\*{2}(?!\*)(.+?)(?<!\*)\*{2}(?!\*)"
ITALIC = r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)"
AUDIO = r"!\[type:audio\]\((.+?)\)"
RULE = r"^(-_*){3,}"
LINE_BREAK = r"<br/?>"

# code. the code of a block is between two fences
CODE_FENCE = "```"
CODE_BLOCK = r"```((.|\n)*?)```"
INLINE_CODE = r"`(.+?)`"

# a link: the text, then the target. `!` in front makes an image
LINK = r"(?<!!)\[([^@\n\{\}]+?)\]\((.*?)\)"
IMAGE = r"!\[(.*?)\]\((.*?)\)"
CITATION = r"\[(-?@[^\]]+)\](?!\()"

# headings. HEADING is the form of md2tex: `#` and text with no space between is a heading.
# HEADING_STRICT is the CommonMark form: a space or the end of the line follows the `#` characters.
# a `>` can come before the `#`, as a heading can be in a block quote
HEADING = r"^([\s>]*)(#+)(?!#)"
HEADING_STRICT = r"^([\s>]*)(#+)(?=[ \t]|$)"

# math. INLINE_MATH is the form of md2tex: any text between two `$`.
# INLINE_MATH_STRICT is the form of Pandoc: a character that is not a space follows the first `$` and comes before
# the second `$`, a digit does not follow the second `$`, and `\$` is a dollar sign
BLOCK_MATH = r"\$\$(.+?)\$\$"
INLINE_MATH = r"(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)"
INLINE_MATH_STRICT = r"(?<![\\$])\$(?=[^\s$])([^$]+?)(?<=[^\s\\])\$(?![$\d])"

# an insertion point: a line with only an HTML comment like `<!-- md2misc: name -->`
INSERTION = r"^[ \t]*<!--\s*md2misc:\s*([\w-]+)\s*-->[ \t]*$"

# the token that stands for a math expression until the text is finished. it has only letters and digits, thus
# no other step of the conversion changes it
MATH_TOKEN = "MDMISCMATH{}TOKEN"
MATH_TOKEN_REGEX = r"MDMISCMATH\d+TOKEN"

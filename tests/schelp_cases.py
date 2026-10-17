"""
Markdown cases for the tests of the schelp output.
"""

# Markdown that has no schelp form: the construct that the error names, and its line.
UNSUPPORTED = [
    ("# One\n\nText.\n\n# Two\n", "second level 1 heading", 5),
    ("# Heading with *italics*\n", "heading", 1),
    ("---\nsummary: A\n---\n\n## Section\n\n> Not an alert.\n", "block quote", 7),
    ("---\nsummary: A\nauthor: Me\n---\n", "front matter key `author`", 3),
    ("---\nsummary: [A, B]\n---\n", "front matter key `summary` with a list", 2),
    ("---\nsummary A\n---\n", "front matter line", 2),
    ("## Heading with *italics*\n", "heading", 1),
    ("Text.\n\n## Heading with `code`\n", "heading", 3),
    ("## Heading with $x$\n", "heading", 1),
    ("Text.\n\n> A block quote\n", "block quote", 3),
    ("> [!NOTE]\n> Fine.\n\n> Not fine.\n", "block quote", 4),
    ("Text with [a page](other.md).\n", "link that is not an http URL", 1),
    ("Text.\n\nSee [@doe1999].\n", "citation", 3),
    ("![An image](image.png)\n", "image", 1),
    ("![type:audio](sound.wav)\n", "audio file", 1),
    ("Above.\n\n---\n\nBelow.\n", "horizontal rule", 3),
    ("Text.\n\n```supercollider title=\"Example\"\nx = 1;\n```\n", "code block title", 3),
    ("```sc hl_lines=\"1\"\nx = 1;\n```\n", "highlighted lines", 1),
    ("Use **`code` in bold**.\n", "code inside bold or italic text", 1),
    ("A line<br>break.\n", "line break", 1),
    ("Text.\n\n```\n# Fine in code\n> Fine in code\n```\n\n> Not in code.\n", "block quote", 8),
    ("> [!FOO]\n> An alert that is not known.\n", "block quote", 1),
    ("> ```\n> x = 1;\n> ```\n", "block quote", 1),
    ("Text **see [a page](https://a.org)** here.\n", "link or footnote inside bold or italic text", 1),
    ("Text *with a note[^1]* here.\n\n[^1]: The note.\n", "link or footnote inside bold or italic text", 1),
    ("Text.\n\n## See [a page](https://a.org)\n", "link or footnote in a heading", 3),
    ("## A heading[^1]\n\n[^1]: The note.\n", "link or footnote in a heading", 1),
    ("# A title with [a link](sc:Classes/SinOsc)\n", "link or footnote in a heading", 1),
    ("See [the C# guide](https://example.com).\n", "`#` in the text of a link", 1),
    ("See [a part](https://example.com/a#b#c).\n", "link with more than one `#`", 1),
    ("See [a method](sc:Classes/SinOsc#a#b).\n", "link with more than one `#`", 1),
]

# Markdown that has no schelp form, which the converters take for text: only the check of the source stops at it.
SOURCE_ONLY = [
    ("* One\n* Two\n", "list with `*` or `+` marks", 1),
    ("Text.\n\n+ One\n", "list with `*` or `+` marks", 3),
    ("1) One\n2) Two\n", "numbered list with `)`", 1),
    ("Above.\n\n***\n\nBelow.\n", "horizontal rule", 3),
    ("Above.\n\n_ _ _\n\nBelow.\n", "horizontal rule", 3),
    ("A title\n=======\n\nText.\n", "heading underlined with `=` or `-`", 2),
    ("Text.\n\nA title\n-------\n", "heading underlined with `=` or `-`", 4),
    ("Text.\n\n| a | b |\n|---|---|\n| 1 | 2 |\n", "table", 3),
    ("See <https://example.com>.\n", "link in `<` and `>`", 1),
    ("Mail <me@example.com>.\n", "link in `<` and `>`", 1),
    ("Press <kbd>Ctrl</kbd>.\n", "HTML tag", 1),
    ("Text.\n\n<!-- A comment. -->\n", "HTML comment", 3),
    ("Text.[^1]\n\n[^1]: Line one\n  and line two.\n", "footnote with more than one line", 3),
    ("Text.[^1]\n\n[^1]: Paragraph one.\n\n    Paragraph two.\n", "footnote with more than one line", 3),
]

# Markdown that only the writers of the backend stop at, thus the error has no line.
WRITER_ONLY = [
    ("Text with **bold $x$ math**.\n", "math inside bold or italic text"),
    ("Text with **bold *italic* inside**.\n", "bold text and italic text inside each other"),
    ("Text with *italic **bold** inside*.\n", "bold text and italic text inside each other"),
]

# Problems with the document as a whole: Markdown, arguments of the command and the text that the error must hold.
DOCUMENT_ERRORS = [
    ("---\nsummary: A\n---\n\n## Section\n", [], "needs a title or a class"),
    ("## Section\n", ["--meta", "summary"], "is not of the form KEY=VALUE"),
    ("## Section\n", ["--meta", "colour=red"], "front matter key `colour`"),
    ("## Section\n", ["--insert", "classmethods=nofile.schelp"], "was not found"),
    ("## Section\n", ["--insert", "classmethods={file}"], "has no insertion point for: classmethods"),
    ("---\ntitle: A\nsummary: Bars || here\n---\n\n## Section\n", [], "`##` or `||` in the value of `summary`"),
    ("## Section\n", ["--meta", "title=A ## B"], "`##` or `||` in the value of `title`"),
]

# Markdown that is fine, although it looks like an unsupported construct.
SUPPORTED = [
    "```\n# A comment in code\n> Not a quote\n---\n![x](y)\n```\n",
    "Inline code `<br>` and `[@key]` and `![x](y)`.\n",
    "---\ntitle: Front matter\n---\n\n## Section\n",
    "> [!WARNING]\n> A warning.\n",
    "A link to [a class](sc:Classes/SinOsc) and to [the web](https://example.com).\n",
    "# A title\n\nText.\n",
    "```\n<!-- md2misc: classmethods -->\n```\n",
    "#1 is not a heading, as there is no space after the `#`.\n",
    "It costs $5 and $10, and \\$x\\$ is not math.\n",
    "> [!NOTE]\n> Try this:\n> ```\n> x = 1;\n> ```\n> And then this.\n",
    "Text with a < b > c and C# and F#.\n",
    "A link to [Classes/SinOsc#*ar](sc:Classes/SinOsc#*ar), which has the address as its text.\n",
    "Text.[^1]\n\n[^1]: A note.\n[^2]: Another note.\n",
    "Text.\n\n= is a sign, after an empty line.\n",
]

# Markdown, and the parts of the HTML page that SCDoc must make from the schelp output. The cases of SUPPORTED are
# rendered too, and must give no error.
RENDERS = [
    ("**Note:** text.\n", ["<strong>Note:</strong> text."]),
    ("*Note:* text.\n", ["<em>Note:</em> text."]),
    ("Use `foo:`: please.\n", ["<code>foo:</code>: please."]),
    ("A path `C:\\` here.\n", ["<code>C:\\</code> here."]),
    ("[Note:](https://example.com) text.\n", ['<a href="https://example.com">Note:</a> text.']),
    ("Math $a:$ here.\n", ["<span class='math'>a:</span> here."]),
    ("Text.[^1]\n\n[^1]: A note that ends with a colon:\n", ["A note that ends with a colon:</div>"]),
    ("**Two colons::** here.\n", ["<strong>Two colons::</strong> here."]),
    ("# A::B\n\nText.\n", ["<h1>A::B"]),
    ("> [!NOTE]\n> Try this:\n> ```\n> x = 1;\n> ```\n> And then this.\n",
     ["<textarea class='editor'>x = 1;</textarea>", "And then this."]),
    ("It costs $5 and $10, and \\$x\\$ is not math.\n", ["It costs $5 and $10, and $x$ is not math."]),
    ("#1 is text.\n", ["<p>#1 is text."]),
    ("Math $a::b$ in text.\n", ["<span class='math'>a::b</span>"]),
    ("Before.\n\n$$\nx\n::\ny\n$$\n\nAfter.\n", ["x\n::\ny"]),
    ("Use `a::b` and `x\\` here.\n", ["<code>a::b</code>", "<code>x\\</code> here."]),
    ("## Section: with a colon\n\nText.\n", ["<h2>Section: with a colon</h2>"]),
    ("Term:\n:   A definition that ends with a colon:\n\nAfter.\n", ["<dt>Term:<dd>A definition that ends with a colon:"]),
]

# Attribution of the test fixtures

The fixtures whose names start with `book-` are pages of the book *Komposition og lydproduktion med SuperCollider*, converted for testing. Each `book-*.md` file is a page after the book's own preprocessing; each `.tex` file is the output of the converter for it.

- Work: [Komposition og lydproduktion med SuperCollider](https://sc.anderseskildsen.eu), © 2022-2025 [Anders Eskildsen](https://anderseskildsen.eu)
- Licence: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)
- Source: the book repository at commit `8896a4c` (2025-06-25)
- Changes: the build-private `!!!…!!!` markers are removed; mkdocs-specific syntax (content tabs, front matter, the abstract admonition, audio and mermaid blocks) is rewritten by the book build's preprocessing before the page is stored. The `.tex` files are generated.

The pages in these files are shared under the same licence, CC BY-SA 4.0. The licence of the rest of the repository (GPL-3.0) does not apply to them.

`readme.md` is the README of md2tex, as of commit `f90f23b`, and is released under GPL-3.0. The fixtures whose names start with `synthetic-` are written for this repository and are released under GPL-3.0.

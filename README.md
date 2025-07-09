<img src="https://raw.githubusercontent.com/nkato/sql2mermaid/main/img/top-image.png" width="1200px">

---

![PyPI - License](https://img.shields.io/pypi/l/sql2mermaid)
![GitHub Workflow Status (with event)](https://img.shields.io/github/actions/workflow/status/nkato/sql2mermaid/python-tox.yml?event=push&label=pytest%20with%20py39)
![PyPI](https://img.shields.io/pypi/v/sql2mermaid)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/sql2mermaid)

# sql2mermaid

Convert SQL table dependencies to the text of [mermaid.js](https://mermaid.js.org/) style!

# Required

Python >=3.9

## Installation

```shell
pip install sql2mermaid
```

## Getting Started

```python
import sql2mermaid

sql = """
with bar as (select * from baz)
select * from foo inner join bar on foo.id = bar.id
"""

txt = sql2mermaid.convert(sql)
print(txt)
```

Result

```
graph LR

bar([bar])
root([root])

baz[(baz)]
foo[(foo)]

bar --> baz
root --> foo
root --> bar
```

You can get a diagram of the table dependencies by pasting this into [Mermaid Live Editor](https://mermaid.live/), [Diagrams.net (Draw.io)](https://www.draw.io/), etc.

## Options

You can change the name of the root and whether the FROM, JOIN clause is displayed.

<img src="https://raw.githubusercontent.com/nkato/sql2mermaid/main/img/option-example.png" width="1200px">

## How to Develop

If you've installed Poetry on your machine, you can test it by doing the following:

```shell
poetry run tox
```

## Author

- [nkato](https://github.com/nkato)

## License

This project is licensed under the MIT License - see the [LICENSE.md](https://github.com/nkato/sql2mermaid/blob/main/LICENSE.md) for details

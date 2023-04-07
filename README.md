<img src="https://raw.githubusercontent.com/nkato/sql2mermaid/main/img/top-image.png" width="1200px">

---

![tox badge](https://github.com/nkato/sql2mermaid/actions/workflows/python-tox.yml/badge.svg?event=push)

# sql2mermaid

Convert SQL table dependencies to the text of [mermaid.js](https://mermaid.js.org/) style!

## Installation

WIP

## Getting Started

```python
import sql2mermaid

sql = """
with bar as (select * from baz)
select * from foo inner join bar on foo.id = bar.id
"""

txt = sql2mermaid(sql)
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

## Author

- [nkato](https://github.com/nkato)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) for details

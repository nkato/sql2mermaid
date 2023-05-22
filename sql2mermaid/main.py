from typing import Literal, Tuple

import sqlparse

from .dependencies import Dependencies, Dependency
from .tables import Tables
from .utils import is_pre_tables_mark, remove_quotes


def is_ignorable(x: sqlparse.sql.Token) -> bool:
    if x.ttype in (sqlparse.tokens.Newline, sqlparse.tokens.Whitespace, sqlparse.tokens.Comment):
        return True
    elif isinstance(x, sqlparse.sql.Comment) or "Comment" in str(x.ttype):
        return True
    else:
        return False


def analyze_query(query: str, root_name: str) -> Tuple[Tables, Dependencies]:
    tables = Tables()
    tables.add(root_name)
    dependencies = Dependencies()

    current_table = ""
    current_indent_level = 0
    is_in_with = False

    # Get flattened tokens by parsing SQL queries.
    parsed = [x for x in sqlparse.parse(query)[0].flatten() if not is_ignorable(x)]

    for i, token in enumerate(parsed):
        if token.ttype is sqlparse.tokens.Keyword.CTE:  # WITH clause
            is_in_with = True
        elif token.value == "(":
            current_indent_level += 1
        elif token.value == ")":
            current_indent_level -= 1
        elif token.ttype is sqlparse.tokens.Name and current_indent_level == 0 and is_in_with:  # Sub table
            table_name = remove_quotes(token.value)
            tables.add(table_name)
            current_table = table_name
        elif token.ttype is sqlparse.tokens.Keyword and is_pre_tables_mark(token.value, parsed[i - 3].value):  # FROM or JOIN
            table_name = remove_quotes(parsed[i + 1].value)
            if not table_name == "(":
                tables.add(table_name)
                dep = Dependency(current_table, token.value, table_name)
                if dep not in dependencies:
                    dependencies.add(dep)
        elif token.ttype is sqlparse.tokens.Keyword.DML and token.value.upper() == "SELECT" and current_indent_level == 0:
            is_in_with = False
            current_table = root_name

    return tables, dependencies


def extract_leafs(tables: Tables, dependencies: Dependencies) -> Tuple[Tables, Tables]:
    internals = Tables()
    leafs = tables.copy()
    for dep in dependencies:
        if dep.start in leafs:
            leafs.remove(dep.start)
            internals.add(dep.start)
    return internals, leafs


def generate_mermaid(
    internals: Tables, leafs: Tables, dependencies: Dependencies, display_join: Literal["none", "upper", "lower"]
) -> str:
    res = "graph LR\n\n"
    for table in internals:
        res += f"{table}([{table}])\n"

    res += "\n"
    for table in leafs:
        res += f"{table}[({table})]\n"

    res += "\n"
    for dep in dependencies:
        mark = ""
        if display_join == "upper":
            mark = f"-- {dep.mark.upper()} "
        elif display_join == "lower":
            mark = f"-- {dep.mark.lower()} "
        res += f"{dep.start} {mark}--> {dep.end}\n"

    return res


def convert(query: str, *, root_name: str = "root", display_join: Literal["none", "upper", "lower"] = "none") -> str:
    tables, dependencies = analyze_query(query, root_name)
    internals, leafs = extract_leafs(tables, dependencies)
    mermaid_text = generate_mermaid(internals, leafs, dependencies, display_join)
    return mermaid_text

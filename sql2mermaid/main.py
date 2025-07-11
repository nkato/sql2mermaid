from typing import Literal

import sqlparse

from .dependencies import Dependencies, Dependency
from .tables import Tables
from .utils import is_pre_tables_mark, remove_quotes


def is_ignorable(x: sqlparse.sql.Token) -> bool:
    """Check if a token should be ignored (whitespace, newline, comment)."""
    if x.ttype in (sqlparse.tokens.Newline, sqlparse.tokens.Whitespace, sqlparse.tokens.Comment):
        return True
    return isinstance(x, sqlparse.sql.Comment) or "Comment" in str(x.ttype)


def split_statements(query: str) -> list[str]:
    """Split a query into individual SQL statements."""
    statements = []
    parsed = sqlparse.parse(query)

    for statement in parsed:
        stmt_str = str(statement).strip()
        if stmt_str:
            statements.append(stmt_str)

    return statements


def is_select_statement(statement: str) -> bool:
    """Check if a statement is a SELECT statement."""
    parsed = sqlparse.parse(statement)
    if not parsed:
        return False

    # Get the first meaningful token
    for token in parsed[0].tokens:
        if not is_ignorable(token):
            if token.ttype is sqlparse.tokens.Keyword.DML:
                return token.value.upper() == "SELECT"
            elif token.ttype is sqlparse.tokens.Keyword.CTE:
                return True  # WITH clause followed by SELECT
            else:
                return False

    return False


def extract_table_name(tokens: list[sqlparse.sql.Token], start_index: int) -> str:
    """Extract table name from tokens, handling dotted table names."""
    if start_index >= len(tokens):
        return ""

    table_parts = []
    i = start_index

    # First token should be a Name token
    if tokens[i].ttype is sqlparse.tokens.Name:
        table_parts.append(remove_quotes(tokens[i].value))
        i += 1
    else:
        return ""

    # Check for dotted continuation
    while i < len(tokens) - 1:
        if tokens[i].value == "." and tokens[i + 1].ttype is sqlparse.tokens.Name:
            table_parts.append(remove_quotes(tokens[i + 1].value))
            i += 2
        else:
            break

    return ".".join(table_parts)


def analyze_query(query: str, root_name: str) -> tuple[Tables, Dependencies]:
    """Analyze a SQL query and extract tables and their dependencies."""
    tables = Tables()
    tables.add(root_name)
    dependencies = Dependencies()

    current_table = ""
    current_indent_level = 0
    is_in_with = False
    with_indent_level = -1  # Track the indent level where WITH was found
    cte_definition_level = -1  # Track the indent level of current CTE definition
    last_token_was_from_or_join = False  # Track if the last keyword was FROM or JOIN
    last_token_was_with_or_comma = False  # Track if the last token was WITH or comma
    is_in_select = False  # Track if we're inside a SELECT statement
    select_indent_level = -1  # Track the indent level where SELECT was found

    # Get flattened tokens by parsing SQL queries.
    parsed = [x for x in sqlparse.parse(query)[0].flatten() if not is_ignorable(x)]

    for i, token in enumerate(parsed):
        if token.ttype is sqlparse.tokens.Keyword.CTE:  # WITH clause
            is_in_with = True
            with_indent_level = current_indent_level
            last_token_was_with_or_comma = True
        elif token.value == "(":
            current_indent_level += 1
        elif token.value == ")":
            current_indent_level -= 1
            # Reset is_in_with when we leave the WITH clause scope
            if is_in_with and current_indent_level < with_indent_level:
                is_in_with = False
                with_indent_level = -1
            # Reset CTE definition level when we leave the CTE definition
            if cte_definition_level >= 0 and current_indent_level < cte_definition_level:
                cte_definition_level = -1
            # Reset is_in_select when we leave the SELECT scope
            if is_in_select and current_indent_level < select_indent_level:
                is_in_select = False
                select_indent_level = -1
        elif token.value == "," and is_in_with:
            last_token_was_with_or_comma = True
        elif (
            token.ttype is sqlparse.tokens.Name
            and is_in_with
            and (not last_token_was_from_or_join or last_token_was_with_or_comma)
            and (
                not is_in_select or current_indent_level > select_indent_level
            )  # Allow CTE detection if we're in a deeper scope than the current SELECT
        ):  # CTE name
            # Check if this is a CTE definition (not a reference)
            # Look ahead to see if this is followed by 'AS'
            if i + 1 < len(parsed) and parsed[i + 1].ttype is sqlparse.tokens.Keyword and parsed[i + 1].value.upper() == "AS":
                table_name = remove_quotes(token.value)
                tables.add(table_name)
                current_table = table_name
                cte_definition_level = current_indent_level
            last_token_was_with_or_comma = False
        elif token.ttype is sqlparse.tokens.Keyword and is_pre_tables_mark(
            token.value, parsed[i - 3].value if i >= 3 else ""
        ):  # FROM or JOIN
            table_name = extract_table_name(parsed, i + 1)
            if table_name and table_name != "(":
                tables.add(table_name)
                # Use the appropriate source table based on context
                source_table = current_table if current_table else root_name
                dep = Dependency(source_table, token.value, table_name)
                if dep not in dependencies:
                    dependencies.add(dep)
            last_token_was_from_or_join = True
            last_token_was_with_or_comma = False
        elif token.ttype is sqlparse.tokens.Keyword.DML and token.value.upper() == "SELECT":
            # Track that we're in a SELECT statement
            is_in_select = True
            select_indent_level = current_indent_level

            # Only reset WITH scope if we're actually in a WITH clause
            # and the SELECT is at the same or higher level
            if is_in_with and current_indent_level <= with_indent_level:
                is_in_with = False
                current_table = root_name
            elif not is_in_with and current_indent_level == 0:
                current_table = root_name
            # If we're not currently in a WITH clause, don't change current_table
            # This allows nested WITH clauses to work correctly
            last_token_was_from_or_join = False
            last_token_was_with_or_comma = False
        else:
            # Reset the FROM/JOIN flag for non-name tokens
            if token.ttype is not sqlparse.tokens.Name:
                last_token_was_from_or_join = False
                last_token_was_with_or_comma = False

    return tables, dependencies


def extract_leafs(tables: Tables, dependencies: Dependencies) -> tuple[Tables, Tables]:
    """Separate tables into internal nodes and leaf nodes based on dependencies."""
    internals = Tables()
    leafs = tables.copy()
    for dep in dependencies:
        if dep.start in leafs:
            leafs.remove(dep.start)
            internals.add(dep.start)
    return internals, leafs


def generate_mermaid(
    internals: Tables,
    leafs: Tables,
    dependencies: Dependencies,
    display_join: Literal["none", "upper", "lower"],
) -> str:
    """Generate Mermaid graph syntax from tables and dependencies."""

    def get_display_name(table_name: str) -> str:
        """Get display name for a table. Convert root1, root2, etc. to 'root'"""
        if table_name.startswith("root") and len(table_name) > 4 and table_name[4:].isdigit():
            return "root"
        return table_name

    res = "graph LR\n\n"
    for table in internals:
        display_name = get_display_name(table)
        res += f"{table}([{display_name}])\n"

    res += "\n"
    for table in leafs:
        display_name = get_display_name(table)
        res += f"{table}[({display_name})]\n"

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
    """Convert SQL query to Mermaid graph, handling multiple SELECT statements."""
    # Split the query into individual statements
    statements = split_statements(query)

    # Filter out non-SELECT statements
    select_statements = [stmt for stmt in statements if is_select_statement(stmt)]

    if not select_statements:
        # If no SELECT statements, fall back to original behavior
        tables, dependencies = analyze_query(query, root_name)
        internals, leafs = extract_leafs(tables, dependencies)
        return generate_mermaid(internals, leafs, dependencies, display_join)

    # Process multiple SELECT statements
    all_tables = Tables()
    all_dependencies = Dependencies()

    for i, stmt in enumerate(select_statements):
        current_root = f"{root_name}{i+1}" if len(select_statements) > 1 else root_name
        tables, dependencies = analyze_query(stmt, current_root)

        # Merge tables and dependencies
        for table in tables:
            all_tables.add(table)
        for dep in dependencies:
            all_dependencies.add(dep)

    internals, leafs = extract_leafs(all_tables, all_dependencies)
    return generate_mermaid(internals, leafs, all_dependencies, display_join)

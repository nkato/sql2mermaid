def is_pre_tables_mark(x: str, y: str) -> bool:
    if x.upper() == "FROM" and y.upper() != "EXTRACT":
        return True
    return "JOIN" in x.upper()


def remove_quotes(x: str) -> str:
    quotes = ["`", "'", '"']
    return x[1:-1] if x[0] in quotes and x[-1] in quotes else x

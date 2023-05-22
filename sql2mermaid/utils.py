def is_pre_tables_mark(x: str, y: str) -> bool:
    if x.upper() == "FROM" and not y.upper() == "EXTRACT":
        return True
    elif "JOIN" in x.upper():
        return True
    return False


def remove_quotes(x: str) -> str:
    quotes = ["`", "'", '"']
    if x[0] in quotes and x[-1] in quotes:
        return x[1:-1]
    else:
        return x

from collections.abc import Iterator


class Tables:
    def __init__(self) -> None:
        self.values: list[str] = []

    def __call__(self) -> list[str]:
        return self.values

    def __iter__(self) -> Iterator[str]:
        yield from self.values

    def add(self, x: str, /) -> None:
        if x not in self.values:
            self.values.append(x)

    def remove(self, x: str) -> None:
        if x in self.values:
            self.values.remove(x)

    def copy(self) -> "Tables":
        new_table = Tables()
        new_table.values = self.values.copy()
        return new_table

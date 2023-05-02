from collections.abc import Iterator
from dataclasses import dataclass


@dataclass
class Dependency:
    start: str
    mark: str
    end: str


class Dependencies:
    def __init__(self) -> None:
        self.values: list[Dependency] = []

    def __call__(self) -> list[Dependency]:
        return self.values

    def __iter__(self) -> Iterator[Dependency]:
        yield from self.values

    def add(self, x: Dependency, /) -> None:
        if x not in self:
            self.values.append(x)

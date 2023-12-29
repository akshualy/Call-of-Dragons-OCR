from abc import ABC, abstractmethod


class Exporter(ABC):
    @abstractmethod
    def export(self, user_data: dict[int, dict[str, int | str]]):
        pass

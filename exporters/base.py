from abc import ABC
from abc import abstractmethod


class AbstractExporter(ABC):
    @abstractmethod
    def export(self, user_data: dict[int, dict[str, int | str]]):
        pass

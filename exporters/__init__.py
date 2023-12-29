from enum import Enum

from .base import Exporter
from .csv_file import CsvExporter


class ExporterType(Enum):
    CSV = "csv"


def get_exporter(exporter_type: ExporterType = ExporterType.CSV) -> Exporter:
    match exporter_type:
        case ExporterType.CSV | _:
            return CsvExporter()

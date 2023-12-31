from enum import StrEnum

from .base import AbstractExporter
from .csv_file import CsvExporter
from .google_sheets import GoogleSheetsExporter


class ExporterType(StrEnum):
    CSV = "csv"
    GOOGLE_SHEETS = "google_sheets"


def get_exporter(exporter_type: ExporterType = ExporterType.CSV) -> AbstractExporter:
    match exporter_type:
        case ExporterType.GOOGLE_SHEETS:
            return GoogleSheetsExporter()
        case ExporterType.CSV | _:
            return CsvExporter()

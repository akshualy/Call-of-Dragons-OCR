from datetime import datetime

from exporters import AbstractExporter
from logic.logic import ALLIANCE_INFORMATION


class CsvExporter(AbstractExporter):
    def export(self, user_data: dict[int, dict[str, int | str]]):
        file_name = (
            f"{datetime.now().strftime('%Y-%m-%d_%H-%M')}_"
            f"{ALLIANCE_INFORMATION.alliance_name.replace(' ', '-')}"
        )
        with open(file_name + ".csv", "w", encoding="utf-8") as csv:
            csv.write("Lord ID,Name,Power,Merit\n")
            for lord_id, name_power_merit in user_data.items():
                csv.write(
                    f"{lord_id},"
                    f"{name_power_merit['name']},"
                    f"{name_power_merit['power']},"
                    f"{name_power_merit['merit']}\n"
                )

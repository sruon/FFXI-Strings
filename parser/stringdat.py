from pathlib import Path

from models.strings import ParsedStringDat


class StringDatParser:
    @staticmethod
    def parse_file(file_path: str | Path, encoding: str = "utf-8") -> ParsedStringDat:
        with open(file_path, "rb") as f:
            data = f.read()
        return ParsedStringDat.from_raw_data(data, encoding)

    @staticmethod
    def parse_file_english(file_path: str | Path) -> ParsedStringDat:
        return StringDatParser.parse_file(file_path, encoding="utf-8")

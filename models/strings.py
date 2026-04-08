from dataclasses import dataclass


@dataclass
class ParsedString:
    index: int
    offset: int
    text: str


@dataclass
class ParsedStringDat:
    entry_count: int
    strings: list[ParsedString]

    @classmethod
    def from_raw_data(cls, raw_data: bytes, encoding: str = "utf-8") -> "ParsedStringDat":
        if len(raw_data) < 8:
            raise ValueError("File too small")

        file_size_marker = int.from_bytes(raw_data[0:4], "little")
        expected_marker = 0x10000000 + len(raw_data) - 4
        if file_size_marker != expected_marker:
            raise ValueError(f"Invalid file size marker: {file_size_marker:08X}")

        first_text_pos = int.from_bytes(raw_data[4:8], "little") ^ 0x80808080
        if first_text_pos % 4 != 0 or first_text_pos > len(raw_data) or first_text_pos < 8:
            raise ValueError(f"Invalid first text position: {first_text_pos}")

        entry_count = first_text_pos // 4

        offsets = [first_text_pos]
        for i in range(1, entry_count):
            offset_pos = 4 + (i * 4)
            if offset_pos + 4 > len(raw_data):
                break
            offsets.append(int.from_bytes(raw_data[offset_pos:offset_pos + 4], "little") ^ 0x80808080)

        offsets.append(len(raw_data) - 4)
        offsets.sort()

        strings = []
        for i in range(entry_count):
            if offsets[i] < 4 * entry_count or offsets[i] >= len(raw_data) - 4:
                continue

            start_pos = offsets[i] + 4
            end_pos = (offsets[i + 1] + 4) if i + 1 < len(offsets) else len(raw_data)
            if start_pos >= len(raw_data) or end_pos > len(raw_data):
                continue

            try:
                raw_bytes = raw_data[start_pos:end_pos]
                decoded = bytes(b - 0x80 if b >= 0x80 else b for b in raw_bytes).rstrip(b"\x00")
                text = decoded.decode(encoding, errors="replace")
                strings.append(ParsedString(index=i, offset=offsets[i], text=text))
            except Exception:
                pass

        return cls(entry_count=entry_count, strings=strings)

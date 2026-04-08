"""Format FFXI dialog strings to match POLUtils + sanitize_pol_string output."""

import re


def _skip(pos, text, n):
    return min(pos + n, len(text))


def format_string(text):
    result = []
    pos = 0
    in_selection = False

    while pos < len(text):
        b = ord(text[pos])

        if b == 0x07:
            if pos + 1 < len(text) and ord(text[pos + 1]) == 0x32:
                if pos + 3 < len(text) and text[pos + 2:pos + 4] == "nd":
                    result.append(" ")
                    pos += 1
                else:
                    pos += 2
            elif pos + 1 < len(text) and ord(text[pos + 1]) == 0x33:
                if pos + 3 < len(text) and text[pos + 2:pos + 4] == "rd":
                    result.append(" ")
                    pos += 1
                else:
                    pos += 2
            else:
                result.append("/" if in_selection else " ")
                pos += 1

        elif b == 0x08:
            result.append("%")
            pos += 1
        elif b == 0x09:
            pos += 1
        elif b == 0x0A:
            result.append("#")
            pos = _skip(pos, text, 2)
        elif b == 0x0B:
            pos += 1
        elif b in (0x0C, 0x19, 0x1A):
            pos = _skip(pos, text, 2)
        elif b == 0x1C:
            result.append("%")
            pos = _skip(pos, text, 2)
        elif b == 0x1E:
            pos = _skip(pos, text, 3 if pos + 1 < len(text) and ord(text[pos + 1]) == 0x1F else 2)
        elif b == 0x1F:
            pos = _skip(pos, text, 2)

        elif b == 0x7F:
            if pos + 1 >= len(text):
                pos += 1
                continue
            sub = ord(text[pos + 1])
            if sub == 0x31:
                if in_selection:
                    in_selection = False
                pos = _skip(pos, text, 3)
            elif sub == 0x92:
                result.append("[/")
                in_selection = True
                pos = _skip(pos, text, 3)
            else:
                pos = _skip(pos, text, 3 if sub != 0x85 else 2)

        elif b == 0x01:
            found = False
            for j in range(pos + 1, min(pos + 14, len(text))):
                if ord(text[j]) == 0x02:
                    if j <= pos + 1 or ord(text[j - 1]) != 0x29:
                        result.append("%")
                    pos = min(j + 4, len(text))
                    found = True
                    break
            if not found:
                pos += 1

        elif b == 0x05:
            result.append("%")
            pos += 1
            while pos < len(text) and 0x20 <= ord(text[pos]) < 0x7F:
                pos += 1
        elif b == 0x11:
            result.append("%")
            pos += 1

        elif b == 0x00 or b < 0x20:
            pos += 1
        elif 0x20 <= b < 0x7F:
            result.append(text[pos])
            pos += 1
        else:
            pos += 1

    raw = re.sub(r" +", " ", "".join(result))
    return "".join(c for c in raw if ord(c) >= 0x20).strip()

'''Early vendor-specific parser integration placeholder.

The previous version contained incomplete Python syntax. This Alpha-safe version
keeps supplier detection operational while detailed line-item parsing continues.
'''


def parse_bullseye(lines, count=0):
    return {
        "supplier": "Bullseye Glass Co.",
        "start_index": count,
        "raw_lines": list(lines),
    }


def parse(lines):
    for index, value in enumerate(lines):
        if value == "Bullseye Glass Co.":
            return parse_bullseye(lines, index)
        if value == "Mountain Glass":
            return {"supplier": "Mountain Glass", "start_index": index, "raw_lines": list(lines)}
    return {"supplier": None, "start_index": None, "raw_lines": list(lines)}

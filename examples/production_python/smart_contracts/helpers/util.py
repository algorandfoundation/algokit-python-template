from pathlib import Path

import tomllib


def find_app_spec_file(output_dir: Path) -> str | None:
    for file in output_dir.iterdir():
        if file.is_file() and file.suffixes == [".arc32", ".json"]:
            return file.name
    return None


def find_pyproject_version(pyproject_toml: Path) -> str | None:
    try:
        data = tomllib.load(open(pyproject_toml, "rb"))
        return data.get("tool", {}).get("poetry", {}).get("version")
    except (FileNotFoundError, tomllib.TOMLDecodeError):
        return None

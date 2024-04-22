from pathlib import Path

import tomllib


def find_app_spec_file(output_dir: Path) -> str | None:
    for file in output_dir.iterdir():
        if file.is_file() and file.suffixes == [".arc32", ".json"]:
            return file.name
    return None


def find_pyproject_version(pyproject_toml: Path) -> str | None:
    with open(pyproject_toml, "rb") as f:
        content = tomllib.load(f)
    return (
        content["tool"]["poetry"]["version"]
        if "tool" in content
        and "poetry" in content["tool"]
        and "version" in content["tool"]["poetry"]
        else None
    )

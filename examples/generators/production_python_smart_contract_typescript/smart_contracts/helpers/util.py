from pathlib import Path


def find_app_spec_file(output_dir: Path) -> str | None:
    for file in output_dir.iterdir():
        if file.is_file() and file.suffixes == [".arc32", ".json"]:
            return file.name
    return None


def find_app_spec_files(output_dir: Path) -> list[str]:
    return [file.name for file in output_dir.glob("*.arc32.json")]

import re
import shutil
import subprocess
import tempfile
from collections.abc import Iterator
from pathlib import Path

import pytest
import yaml

commit_pattern = re.compile(r"^_commit: .*", flags=re.MULTILINE)
src_path_pattern = re.compile(r"_src_path: .*")
tests_path = Path(__file__).parent
root = tests_path.parent
generated_folder = "tests_generated"
generated_root = root / generated_folder
DEFAULT_PARAMETERS = {
    "author_name": "None",
    "author_email": "None",
}
config_path = Path(__file__).parent.parent / "pyproject.toml"
RUFF_FORMATTER_ARGS = ["ruff", "format", "--check", "--config", str(config_path), "."]
RUFF_ARGS = ["ruff", "--diff", "--config", str(config_path), "."]
MYPY_ARGS = [
    "mypy",
    "--ignore-missing-imports",  # TODO: only ignore missing typed clients in config.py
    ".",
]


def _load_copier_yaml(path: Path) -> dict[str, str | bool | dict]:
    with path.open("r", encoding="utf-8") as stream:
        return yaml.safe_load(stream)


@pytest.fixture(autouse=True, scope="module")
def working_dir() -> Iterator[Path]:
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp:
        working_dir = Path(temp) / "template"
        working_generated_root = working_dir / generated_folder
        shutil.copytree(root, working_dir)
        subprocess.run(["git", "add", "-A"], cwd=working_dir, check=False)
        subprocess.run(
            ["git", "commit", "-m", "draft changes", "--no-verify"],
            cwd=working_dir,
            check=False,
        )

        yield working_dir

        for src_dir in working_generated_root.iterdir():
            if not src_dir.is_dir():
                continue

            dest_dir = generated_root / src_dir.stem
            shutil.rmtree(dest_dir, ignore_errors=True)
            shutil.copytree(src_dir, dest_dir, dirs_exist_ok=True)


def run_init(
    working_dir: Path,
    test_name: str,
    *args: str,
    template_url: str | None = None,
    template_branch: str | None = None,
    answers: dict[str, str] | None = None,
) -> subprocess.CompletedProcess:
    copy_to = working_dir / generated_folder / test_name
    shutil.rmtree(copy_to, ignore_errors=True)
    if template_url is None:
        template_url = str(working_dir)

        if template_branch is None:
            git_output = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=working_dir,
                stdout=subprocess.PIPE,
            )
            template_branch = git_output.stdout.decode("utf-8").strip()

    init_args = [
        "algokit",
        "--verbose",
        "init",
        "--name",
        str(copy_to.stem),
        "--template-url",
        template_url,
        "--UNSAFE-SECURITY-accept-template-url",
        "--defaults",
        "--no-ide",
        "--no-git",
        "--no-bootstrap",
    ]
    answers = {**DEFAULT_PARAMETERS, **(answers or {})}

    for question, answer in answers.items():
        init_args.extend(["-a", question, answer])
    if template_branch:
        init_args.extend(["--template-url-ref", template_branch])
    init_args.extend(args)

    result = subprocess.run(
        init_args,
        input="y",  # acknowledge that input is not a tty
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        cwd=copy_to.parent,
        check=False,
    )

    return result


def check_codebase(working_dir: Path, test_name: str) -> subprocess.CompletedProcess:
    copy_to = working_dir / generated_folder / test_name

    # if successful, normalize .copier-answers.yml to make observing diffs easier
    copier_answers = Path(copy_to / ".copier-answers.yml")
    content = copier_answers.read_text("utf-8")
    content = commit_pattern.sub("_commit: <commit>", content)
    content = src_path_pattern.sub("_src_path: <src>", content)
    copier_answers.write_text(content, "utf-8")

    check_args = [RUFF_FORMATTER_ARGS]

    # Starter template does not have ruff config or mypy config by default
    # so only check for them if the starter template is not used
    processed_questions = _load_copier_yaml(copier_answers)
    if processed_questions["preset_name"] == "production":
        check_args += [RUFF_ARGS, MYPY_ARGS]

    for check_arg in check_args:
        result = subprocess.run(
            check_arg,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=copy_to,
        )
        if result.returncode:
            break

    return result


def run_generator(
    working_dir: Path,
    test_name: str,
    generator_name: str,
    answers: dict[str, str] | None = None,
) -> subprocess.CompletedProcess:
    copy_to = working_dir / generated_folder / test_name

    init_args = [
        "algokit",
        "--verbose",
        "generate",
        str(generator_name),
    ]

    if answers:
        for question, answer in answers.items():
            init_args.extend(["-a", question, answer])

    result = subprocess.run(
        init_args,
        input="y",  # acknowledge that input is not a tty
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        cwd=copy_to.absolute(),
    )

    return result


@pytest.mark.parametrize("language", ["python", "typescript"])
def test_smart_contract_generator_default_starter_preset(
    language: str, working_dir: Path
) -> None:
    test_name = f"test_smart_contract_generator_default_starter_preset_{language}"

    response = run_init(
        working_dir,
        test_name,
        answers={
            "preset_name": "starter",
            "deployment_language": language,
        },
    )
    assert response.returncode == 0, response.stdout

    response = run_generator(
        working_dir,
        test_name,
        "smart-contract",
        {
            "contract_name": "cool_contract",
            "deployment_language": language,
        },
    )
    assert response.returncode == 0, response.stdout

    response = check_codebase(working_dir, test_name)
    assert response.returncode == 0, response.stdout


@pytest.mark.parametrize("language", ["python", "typescript"])
def test_smart_contract_generator_default_production_preset(
    language: str, working_dir: Path
) -> None:
    test_name = f"test_smart_contract_generator_default_production_preset_{language}"

    response = run_init(
        working_dir,
        test_name,
        answers={
            "preset_name": "production",
            "deployment_language": language,
        },
    )
    assert response.returncode == 0, response.stdout

    response = run_generator(
        working_dir,
        test_name,
        "smart-contract",
        {
            "contract_name": "cool_contract",
            "deployment_language": language,
        },
    )
    assert response.returncode == 0, response.stdout

    response = check_codebase(working_dir, test_name)
    assert response.returncode == 0, response.stdout

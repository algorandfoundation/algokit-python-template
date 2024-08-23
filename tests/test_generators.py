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
generated_folder = "examples/generators"
generated_root = root / generated_folder
DEFAULT_PARAMETERS = {
    "author_name": "None",
    "author_email": "None",
}
config_path = Path(__file__).parent.parent / "pyproject.toml"
BUILD_ARGS = ["algokit", "project", "run", "build"]
BUILD_SINGLE_CONTRACT_ARGS = ["algokit", "project", "run", "build", "--", "hello_world"]
TEST_ARGS = ["algokit", "project", "run", "test"]
LINT_ARGS = ["algokit", "project", "run", "lint"]
DEPLOY_ARGS = ["algokit", "project", "deploy", "localnet"]
DEPLOY_SINGLE_CONTRACT_ARGS = [
    "algokit",
    "project",
    "deploy",
    "localnet",
    "--",
    "hello_world",
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
        subprocess.run(["git", "add", "-A"], cwd=working_dir)
        subprocess.run(
            ["git", "commit", "-m", "draft changes", "--no-verify"], cwd=working_dir
        )

        yield working_dir

        for src_dir in working_generated_root.iterdir():
            if not src_dir.is_dir():
                continue

            dest_dir = generated_root / src_dir.stem
            shutil.rmtree(dest_dir, ignore_errors=True)
            shutil.copytree(
                src_dir,
                dest_dir,
                dirs_exist_ok=True,
                ignore=shutil.ignore_patterns(
                    ".*_cache", ".venv", "__pycache__", "node_modules"
                ),
            )


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
        "--no-workspace",
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
    )

    return result


def check_codebase(working_dir: Path, test_name: str) -> subprocess.CompletedProcess:
    copy_to = working_dir / generated_folder / test_name

    # if successful, normalize .copier-answers.yml to make observing diffs easier
    copier_answers = Path(copy_to / ".algokit" / ".copier-answers.yml")
    content = copier_answers.read_text("utf-8")
    content = commit_pattern.sub("_commit: <commit>", content)
    content = src_path_pattern.sub("_src_path: <src>", content)
    copier_answers.write_text(content, "utf-8")

    check_args = [BUILD_ARGS, BUILD_SINGLE_CONTRACT_ARGS]

    processed_questions = _load_copier_yaml(copier_answers)
    if processed_questions["preset_name"] == "production":
        check_args += [LINT_ARGS, TEST_ARGS, DEPLOY_SINGLE_CONTRACT_ARGS, DEPLOY_ARGS]

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
    test_name = f"starter_python_smart_contract_{language}"

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
    test_name = f"production_python_smart_contract_{language}"

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

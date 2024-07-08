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
generated_folder = "examples"
generated_root = root / generated_folder
DEFAULT_PARAMETERS = {
    "author_name": "None",
    "author_email": "None",
}
config_path = Path(__file__).parent.parent / "pyproject.toml"
BUILD_ARGS = ["algokit", "project", "run", "build"]
TEST_ARGS = ["algokit", "project", "run", "test"]
LINT_ARGS = ["algokit", "project", "run", "lint"]


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
    answers["deployment_language"] = "python"

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

    if result.returncode:
        return result
    # if successful, normalize .copier-answers.yml to make observing diffs easier
    copier_answers = Path(copy_to / ".algokit" / ".copier-answers.yml")
    content = copier_answers.read_text("utf-8")
    content = commit_pattern.sub("_commit: <commit>", content)
    content = src_path_pattern.sub("_src_path: <src>", content)
    copier_answers.write_text(content, "utf-8")

    check_args = [BUILD_ARGS]

    processed_questions = _load_copier_yaml(copier_answers)
    if processed_questions["preset_name"] == "production":
        check_args += [LINT_ARGS, TEST_ARGS]

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

    # Remove .algokit generators folder to avoid polluting the git history
    shutil.rmtree(copy_to / ".algokit", ignore_errors=True)

    # Check if .idea folder exists and if so modify os specific SDK_HOME path
    idea_folder = copy_to / ".idea"
    if idea_folder.exists():
        # Iterate over all files in .idea/runConfigurations
        for file in (idea_folder / "runConfigurations").iterdir():
            # Read the file content
            content = file.read_text()
            # Replace the line containing SDK_HOME
            content = re.sub(
                r'<option name="SDK_HOME" value=".*" />',
                '<option name="SDK_HOME" value="$PROJECT_DIR$/.venv/bin/python" />',
                content,
            )
            # Write the modified content back to the file
            file.write_text(content)

    return result


def run_init_kwargs(
    working_dir: Path, **kwargs: str | bool
) -> subprocess.CompletedProcess:
    answers = {k: str(v) for k, v in kwargs.items()}
    name_suffix = "_".join(f"{v}_python" for _, v in answers.items())
    return run_init(working_dir, f"{name_suffix}", answers=answers)


def get_questions_from_copier_yaml(
    allowed_questions: list[str] | None = None,
) -> Iterator[tuple[str, str | bool]]:
    copier_yaml = root / "copier.yaml"
    questions = _load_copier_yaml(copier_yaml)
    for question_name, details in questions.items():
        if allowed_questions and question_name not in allowed_questions:
            continue
        if isinstance(details, dict):
            is_preset_question = question_name == "preset_name"

            if is_preset_question:
                for preset_choice in ["starter", "production"]:
                    yield question_name, preset_choice


@pytest.mark.parametrize(("question_name", "answer"), get_questions_from_copier_yaml())
def test_parameters(working_dir: Path, question_name: str, answer: str | bool) -> None:
    response = run_init_kwargs(working_dir, **{question_name: answer})
    assert response.returncode == 0, response.stdout

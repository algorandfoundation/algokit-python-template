# AlgoKit Official Template for contributors

This repository is a template for creating new AlgoKit projects. It includes a basic structure for creating a Algorand Python based smart contract project.

## Pre-requisites

`poetry install` - Install the dependencies for the project.
`pipx install algokit` - Ensure cli is installed.

## Testing

Ensure localnet is running by executing `algokit localnet reset`.

```bash
poetry run pytest
```

This will regenerate the tests for default `starter` and `production` presets as well as default tests for `generators` available on the template.

## Development

### Manual

```bash
algokit -v init --name playground --no-git --UNSAFE-SECURITY-accept-template-url --template-url . --template-url-ref HEAD --no-bootstrap
```

To generate a dummy project into the `playground` folder. This is useful for testing the template to quickly preview the output of the template before testing via `pytest`.

### Using VSCode Tasks

In VSCode IDE, you can find the tasks in the `.vscode/tasks.json` file. To run them:

1. Open the command palette (`Cmd+Shift+P` on macOS, `Ctrl+Shift+P` on Windows/Linux) and type `> Run Task`
2. Select the task you want to run
3. It will be generated for you under the playground folder

To cleanup the playground folder run dedicated cleanup task.

## Contributing

### Commits

We are using the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/#summary) standard for commit messages. This allows us to automatically generate release notes and version numbers. We do this via [Python Semantic Release](https://python-semantic-release.readthedocs.io/en/latest/) and [GitHub actions](.github/workflows/cd.yaml).

### Guiding Principles

AlgoKit development is done within the [AlgoKit Guiding Principles](https://github.com/algorandfoundation/algokit-cli/blob/main/docs/algokit.md#guiding-principles).

### Pull Requests

1. Submit a pull request to the `main` branch. Fork the repo if you are an external contributor.
2. Ensure that the pull request is up to date with the `main` branch.
3. Ensure that the pull request has a clear title and description.
4. Pass PR reviews and wait for approval.

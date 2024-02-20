# AlgoKit Official Template for contributors

This repository is a template for creating new AlgoKit projects. It includes a basic structure for creating a beaker based smart contract project.

## Pre-requisites

`poetry install` - Install the dependencies for the project.

## Testing

```bash
poetry run pytest
```

This will regenerate the tests for default `starter` and `production` presets as well as default tests for `generators` available on the template.

## Development

```bash
poetry run copier copy . .playground/{some_dummy_folder_name} --vcs-ref=HEAD --trust
```

To generate a dummy project into the `.playground` folder. This is useful for testing the template to quickly preview the output of the template before testing via `pytest`.

## Contributing

### Commits

We are using the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/#summary) standard for commit messages. This allows us to automatically generate release notes and version numbers. We do this via [Python Semantic Release](https://python-semantic-release.readthedocs.io/en/latest/) and [GitHub actions](.github/workflows/cd.yaml).

### Guiding Principles

AlgoKit development is done within the [AlgoKit Guiding Principles](./docs/algokit.md#guiding-principles).

### Pull Requests

1. Submit a pull request to the `main` branch. Fork the repo if you are an external contributor.
2. Ensure that the pull request is up to date with the `main` branch.
3. Ensure that the pull request has a clear title and description.
4. Pass PR reviews and wait for approval.

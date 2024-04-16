# How to Contribute
We welcome collaborators who would like to help expand and improve Bookops-Worldcat. Here are some ways to contribute.

## Report bugs or suggest enhancements
Please use our [Github issue tracker](https://github.com/BookOps-CAT/bookops-worldcat/issues) to submit bug reports or request new features.

## Contribute code or documentation
??? info
    This page contains a draft of our contribution guidelines but there is still more for us to add.
    
    TO DO:

     + Add style guide for documentation
        + docstring style conventions
        + type hints
        + how to build docs after making edits
     + Add CI/CD info

### Style and Requirements
For new code contributions, please use the tools and standards in place for Bookops-Worldcat:

 + Code style:
    + Formatting with [black](https://github.com/psf/black)
    + Linting with [flake8](https://www.flake8rules.com/)
    + Static type checking with [mypy](https://mypy-lang.org/)
 + Dependency management and package publishing with [Poetry](https://github.com/python-poetry/poetry)
 + Documentation written in Markdown using [MkDocs](https://www.mkdocs.org/) and plugins
    + Theme is [Material for MkDocs](https://github.com/squidfunk/mkdocs-material)
    + Versioning maintained with [Mike](https://github.com/jimporter/mike)
    + API Documentation built with [MkAPI](https://github.com/daizutabi/mkapi/)
 + Tests written with [pytest](https://docs.pytest.org/en/8.0.x/)

??? tip
    If you use VS Code there are certain extensions which will automate code formatting and support some of our code style requirements which may make your work easier while contributing to Bookops-Worldcat. Similar extensions are available on other IDEs. Those extensions include:

    + [Black Formatter](https://marketplace.visualstudio.com/items?itemName=ms-python.black-formatter)
    + [Flake8](https://marketplace.visualstudio.com/items?itemName=ms-python.flake8)
    + [Mypy Type Checker](https://marketplace.visualstudio.com/items?itemName=ms-python.mypy-type-checker)
    + [Markdown All in One](https://marketplace.visualstudio.com/items?itemName=yzhang.markdown-all-in-one)

    Additions to add to your settings.json file:
    ```json title="settings.json for VS Code"
    {
        "editor.defaultFormatter": "ms-python.black-formatter",
        "editor.formatOnSave": true,
        "flake8.args": [
            "--max-line-length=88",
        ],
    }
    ```

### Install and Setup
To get started contributing code to Bookops-Worldcat you will need: 

 + Python 3.8 or newer
 + `git`
 + [`poetry`](https://python-poetry.org/docs/#installation)

#### Install Poetry 
Bookops-Worldcat uses `poetry` to manage virtual environments, dependencies, and publishing workflows. We use [`pipx`](https://python-poetry.org/docs/#installing-with-pipx) to run poetry (if you don't have `pipx`, see the [installation instructions](https://pipx.pypa.io/stable/installation/)). For other installation options, see the [`poetry`](https://python-poetry.org/docs/#installation) documentation.

#### Fork the repo
Fork the repository in GitHub and clone your fork locally
```bash
git clone https://github.com/<your username>/bookops-worldcat
cd bookops-worldcat
```
#### Create a new branch for your changes
```bash
git checkout -b new-branch
```
#### Create a virtual environment and install dependencies
Poetry will create a virtual environment, read the `pyproject.toml` and `poetry.lock` files, resolve dependencies, and install them with one command. 
```python
poetry install
```

#### Run tests
Run tests before making changes on your fork.
??? info
    Our live tests are designed to look for API credentials in a specific file/directory in a Windows environment. We will need to refactor the live tests to allow contributors to run live tests with their own API credentials and run live tests in a macOS environment.

```py
# basic usage without webtests
python -m pytest "not webtest"
# with test coverage and without webtests
python -m pytest "not webtest" --cov=bookops_worldcat/
```

### Release Checklist
Any major or minor updates should get a new release in GitHub. Use the following checklist when getting a new update ready for release. For patch updates/bug fixes, follow steps 1-4.

1. Verify `poetry.lock`, `pyproject.toml`, `requirements.txt`, and `dev-requirements.txt` files are up-to-date
     * **`poetry check`** to check that `poetry.lock` and `pyproject.toml` files are synced with 
     * **`poetry update`** to update all packages 
     * or **`poetry update [package1] [ package2]`** to update packages individually
     * **`poetry install`** to install all versions of packages listed in the `pyproject.toml` file
     * Export `requirements.txt` files with [poetry-plugin-export](https://github.com/python-poetry/poetry-plugin-export)
2. Update documentation
    * Update changelog: include version, date, and descriptions of changes
    * Update links within docs if OCLC has made any changes
3. Commit changes to repo
    * Merge all changes into `release/v[version]` branch
    * Ensure tests have run and passed within GitHub Actions
4. Rebuild docs using mike:
    * **`mike --rebase`** to fetch remote version of docs to your local branch (optional)
    * **`mike deploy [version] [alias] --push`** to deploy docs
    * **`mike set-default [version]`** to set new version to default
5. Create a new github release
    * At minimum, include information from changelog in release. Include additional details about changes as appropriate.
6. Build package in poetry
    * `poetry build`
7. Publish to PyPI
    * `poetry publish`

# calisim: Examples and Workshop Material

[![pypi](https://img.shields.io/pypi/v/calisim.svg)](https://pypi.python.org/pypi/calisim)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/Plant-Food-Research-Open/calisim-examples-workshop-material.git/HEAD)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![Build](https://github.com/Plant-Food-Research-Open/calisim-examples-workshop-material/actions/workflows/build.yaml/badge.svg?branch=main)](https://github.com/Plant-Food-Research-Open/calisim-examples-workshop-material/actions/workflows/build.yaml)
[![CodeQL Advanced](https://github.com/Plant-Food-Research-Open/calisim-examples-workshop-material/actions/workflows/codeql.yaml/badge.svg?branch=main)](https://github.com/Plant-Food-Research-Open/calisim-examples-workshop-material/actions/workflows/codeql.yaml)

[**PyPI**](https://pypi.python.org/pypi/calisim)
| [**Documentation**](https://calisim.readthedocs.io)
| [**API**](https://calisim.readthedocs.io/en/latest/api_reference/index.html)
| [**Changelog**](https://calisim.readthedocs.io/en/latest/changelogs/changelog.html)
| [**Examples**](https://github.com/Plant-Food-Research-Open/calisim/tree/main/examples)
| [**Releases**](https://github.com/Plant-Food-Research-Open/calisim/releases)
| [**Docker**](https://github.com/Plant-Food-Research-Open/calisim/pkgs/container/calisim)

*A toolbox for the calibration and evaluation of simulation models.*

# Table of contents

- [calisim: Examples and Workshop Material](#calisim-examples-and-workshop-material)
- [Table of contents](#table-of-contents)
- [Introduction](#introduction)
- [Workshop](#workshop)
  - [Setup](#setup)
    - [Binder](#binder)
    - [Virtual environment](#virtual-environment)
    - [Docker](#docker)

# Introduction

calisim is an open-source, low-code model calibration library that streamlines and standardises your workflows, while aiming to be as flexible and extensible as needed to support more complex use-cases. Using calisim will speed up your experiment cycle substantially and make you more productive.

calisim is primarily a wrapper around popular libraries and frameworks including Optuna, PyMC, scikit-learn, and emcee among many others. The design and simplicity of calisim was inspired by the scikit-learn and PyCaret libraries.

# Workshop

Workshop material for calisim may be found in the [workshop directory.](workshop)

This workshop material covers the following example models:

1. JFruit2
2. TEgenomeSimulator

We will work though basic examples for optimisation and sensitivity analysis, alongside more complex Bayesian computational methods.

[Click this link to launch the workshop material within Binder, which is recommended for users who do not wish to configure the workshop environment locally.](https://mybinder.org/v2/gh/Plant-Food-Research-Open/calisim-examples-workshop-material.git/HEAD)

## Setup

To setup the workshop material, we will first need to clone the GitHub repo like so:

```
git clone https://github.com/Plant-Food-Research-Open/calisim-examples-workshop-material.git

cd calisim-examples-workshop-material
```

### Binder 

[Click this link to launch the workshop material within Binder.](https://mybinder.org/v2/gh/Plant-Food-Research-Open/calisim-examples-workshop-material.git/HEAD)

Note that you may need to wait roughly 5 minutes for the workshop Docker image to be pulled when first using Binder.

### Virtual environment

To run the workshop material within a Python virtual environment, [first ensure that Poetry (a Python dependency manager) is installed.](https://python-poetry.org/docs)

For this workshop, we will use an older version of Poetry (1.8.5):

```
poetry self update 1.8.5
```

After which, run the following to install all required dependencies:

```
export POETRY_VIRTUALENVS_IN_PROJECT=true # Install .venv your project directory, rather than home directory
poetry install --no-root --with dev,docs
poetry shell
```

Finally, launch JupyterLab in your web browser:

```
jupyter lab
```

### Docker

To run the workshop material within a Docker container, execute the following:

```
docker compose up calisim

# ctrl + C to exit
```

This will launch JupyterLab within your browser.

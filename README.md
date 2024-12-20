# Translatorrrr

This project is a translation tool that helps translate documents while preserving their original formatting.

## Features

- Document translation with format preservation
- Support for multiple file formats
- Environment-based configuration

## Setup

1. Clone the repository
2. Create a `.env` file based on the `.env.example` template
3. Install the required dependencies:

```bash
uv venv
uv pip install .
```
or

1. install this project as a package

```bash
uv add git+https://github.com/GrahLnn/translatorrrr.git
pip install git+https://github.com/GrahLnn/translatorrrr.git
```

2. Create a `.env` file based on the `.env.example` template
3. `from translatorrrr import Translator`

## Usage

See `main.py` to start the translation process.

## Environment Variables

Copy `.env.example` to `.env` and configure the following variables:

- API keys for translation services
- Other configuration parameters

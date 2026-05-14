# envcmp

> Diff and audit `.env` files across environments with secret masking.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

---

## Installation

```bash
pip install envcmp
```

---

## Usage

Compare two `.env` files and mask sensitive values:

```bash
envcmp .env.development .env.production
```

**Example output:**

```
KEY                  DEV                  PROD
---------------------------------------------------
DATABASE_URL         ****                 ****
DEBUG                true                 false
NEW_RELIC_KEY        (missing)            ****
LOG_LEVEL            debug                info
```

Mask secrets by default, or show values explicitly with `--no-mask`:

```bash
envcmp .env.staging .env.production --no-mask
```

Audit a single file against a `.env.example` template to find missing or extra keys:

```bash
envcmp --audit .env.example .env.production
```

Output results as JSON for CI pipelines:

```bash
envcmp .env.staging .env.production --format json
```

---

## Features

- Side-by-side diff of any two `.env` files
- Automatic secret masking for keys containing `KEY`, `SECRET`, `TOKEN`, `PASSWORD`, etc.
- Audit mode to detect missing or undocumented variables
- JSON output for easy CI/CD integration

---

## Contributing

Pull requests are welcome. Please open an issue first to discuss any major changes.

---

## License

This project is licensed under the [MIT License](LICENSE).
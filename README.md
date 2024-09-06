# buildwithai

[Add project description here]

## Project Structure

- `src/`: Contains the main source code.
- `tests/`: Contains unit and functional tests.

## Development Setup

### 1. Clone the Repository

```bash
git clone <repository_url>
cd buildwithai
```

### 2. Install Dependencies

```bash
poetry install
```

### 3. Running Tests

Tests are located in the `tests/` directory. To run them, use:

```bash
poetry run pytest
```

### 4. Code Formatting

This project uses `black` for code formatting. It is automatically run on commit via `pre-commit`.

```bash
poetry run black src/ tests/
```

## Branching Strategy

This project uses a relatively simple branching model. The main branches are:
- `main`: The stable release branch.
- `dev`: The development branch.
- `qa`: The quality assurance branch for testing before release.

## Contributing

1. Create a new feature branch from `dev`:
   ```bash
   git checkout dev
   git checkout -b feature/my-feature
   ```
2. Implement your feature or fix.
3. Ensure all tests pass.
4. Commit your changes (formatted with `black`).
5. Push the branch and create a pull request against `dev`.


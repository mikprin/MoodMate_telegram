# Contributing to MoodMate

Thank you for considering contributing to MoodMate! Your support and involvement are greatly appreciated. To make the contribution process seamless, please follow the guidelines below.

## Setting Up Pre-commit Hooks

MoodMate uses pre-commit hooks to maintain code quality and consistency. To install and activate the pre-commit hooks:

1. Ensure you have [pre-commit](https://pre-commit.com/) installed. You can install it via pip:
   ```bash
   pip install pre-commit
   ```

2. Navigate to the root directory of the project and run the following command to install the hooks:
   ```bash
   pre-commit install
   ```

This will automatically run the configured checks in `.pre-commit-config.yaml` before every commit, ensuring code quality.

## Writing Tests

All tests are located in the `./test` directory, which is structured as follows:

```
test
├── resources
└── tests
```

- **`tests/`**: Contains Python test files that test the functionality of the MoodMate project.
- **`resources/`**: Contains auxiliary files and data needed for the tests.

### Running Tests

To ensure your contributions work as intended and do not break existing functionality, write comprehensive tests for any new features or changes you introduce. Place your test files in the `tests` directory.


Run tests with:
```bash
export SQLITE_DB_PATH=./test_db.db && python3 -m pytest -vv test/tests/
```

### Using the Test Environment


### Best Practices

- Write clear, concise, and descriptive test cases.
- Use the resources directory for any additional data files needed for testing.
- Ensure your tests cover edge cases and potential failure scenarios.

## Submitting Contributions

1. Fork the repository and create a new branch for your feature or bugfix. Please follow the **one feature, one branch, one pull request** policy to keep changes modular and reviewable.
2. Commit your changes, ensuring that pre-commit hooks pass successfully.
3. Write or update tests to cover your changes.
4. Submit a pull request to the main repository for review.

Thank you for helping make MoodMate a better project for everyone!

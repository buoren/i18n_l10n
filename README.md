# Hello World NiceGUI App

A simple Hello World application built with NiceGUI for testing i18n/l10n functionality.

## Features

- Interactive Hello World greeting
- Click counter with increment/decrement/reset
- Language selection placeholders (ready for i18n implementation)
- Modern, responsive UI
- Docker support

## Local Development (using Poetry)

### Prerequisites

- Python 3.8+
- Poetry

### Setup

1. Install Poetry if you haven't already:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. Install dependencies:
   ```bash
   poetry install
   ```

3. Run the application:
   ```bash
   poetry run python -m i18n_l10n.main
   ```

   Or use the Poetry script:
   ```bash
   poetry run i18n-app
   ```

4. Open your browser and navigate to `http://localhost:8080`

## Docker Deployment (using pip)

### Build the Docker image

```bash
docker build -t i18n-l10n-app .
```

### Run the container

```bash
docker run -p 8080:8080 i18n-l10n-app
```

The application will be available at `http://localhost:8080`

### Docker Compose (optional)

Create a `docker-compose.yml` file:

```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8080:8080"
    environment:
      - PYTHONUNBUFFERED=1
```

Then run:
```bash
docker-compose up
```

## Project Structure

```
i18n_l10n/
├── i18n_l10n/           # Main application package
│   ├── __init__.py
│   └── main.py          # Main application code
├── pyproject.toml       # Poetry configuration
├── requirements.txt     # pip requirements for Docker
├── Dockerfile          # Docker configuration
├── .dockerignore       # Docker ignore file
└── README.md           # This file
```

## Development

### Database Migrations

The project uses Alembic for database schema management:

```bash
# Create a new migration
./scripts/create_migration.sh "Add new table"

# Apply migrations locally
./scripts/migrate_local.sh upgrade

# Check migration status
./scripts/migrate_local.sh current
```

See [MIGRATIONS.md](MIGRATIONS.md) for detailed migration documentation.

### Code Quality

The project includes development dependencies for code quality:

```bash
# Format code
poetry run black i18n_l10n/

# Lint code
poetry run flake8 i18n_l10n/

# Run tests (when implemented)
poetry run pytest
```

## Future Enhancements

- [ ] Implement actual i18n/l10n support
- [ ] Add more interactive components
- [ ] Implement proper language switching
- [ ] Add database support
- [ ] Add authentication
- [ ] Add API endpoints

## License

This project is open source and available under the MIT License.

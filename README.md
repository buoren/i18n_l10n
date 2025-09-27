# i18n/l10n Translation Management App

A comprehensive translation management application built with NiceGUI, featuring Google OAuth authentication and Google Cloud Translation API integration.

## Features

- **Google OAuth 2.0 Authentication** - Secure login with Google accounts
- **Translation Management** - Admin interface for managing translation tags and texts
- **Google Cloud Translation API** - Automatic translation using Google's translation service
- **Database Integration** - MySQL database with Alembic migrations
- **Cloud Deployment** - Ready for Google Cloud Run deployment
- **Modern UI** - Responsive admin interface built with NiceGUI
- **REST API** - Translation API endpoints for external applications

## Quick Start

### 1. Set up Google OAuth (Required)

Before running the application, you need to configure Google OAuth 2.0:

```bash
# Run the automated OAuth setup
./scripts/setup_google_oauth.sh
```

This will guide you through:
- Enabling required Google Cloud APIs
- Creating OAuth consent screen
- Generating OAuth 2.0 credentials
- Setting up environment variables

### 2. Local Development

#### Prerequisites

- Python 3.8+
- Poetry
- Google Cloud account
- MySQL database (local or Cloud SQL)

#### Setup

1. Install Poetry if you haven't already:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. Install dependencies:
   ```bash
   poetry install
   ```

3. Set up environment variables:
   ```bash
   # The setup script creates a .env file, or create one manually
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Run database migrations:
   ```bash
   ./scripts/migrate_local.sh upgrade
   ```

5. Test the authentication setup:
   ```bash
   python test_auth.py
   ```

6. Run the application:
   ```bash
   poetry run python -m i18n_l10n.main
   ```

7. Open your browser and navigate to `http://localhost:8080/login`

## Cloud Deployment

### Automated Deployment

For a complete deployment to Google Cloud Run with all necessary configurations:

```bash
./scripts/deploy_with_auth.sh
```

This script will:
- Set up Google OAuth 2.0
- Build and push Docker image
- Deploy infrastructure with Terraform
- Configure Cloud Run service
- Test the deployment

### Manual Deployment

1. **Set up Google OAuth** (if not done already):
   ```bash
   ./scripts/setup_google_oauth.sh
   ```

2. **Deploy infrastructure**:
   ```bash
   cd deploy/terraform
   terraform init
   terraform plan
   terraform apply
   ```

3. **Build and deploy application**:
   ```bash
   # Build Docker image
   docker build -t gcr.io/YOUR_PROJECT_ID/i18n-l10n-app .
   
   # Push to Google Container Registry
   docker push gcr.io/YOUR_PROJECT_ID/i18n-l10n-app
   
   # Deploy to Cloud Run
   gcloud run deploy i18n-l10n-app \
     --image gcr.io/YOUR_PROJECT_ID/i18n-l10n-app \
     --platform managed \
     --region europe-north1 \
     --allow-unauthenticated
   ```

## Docker Development

### Build the Docker image

```bash
docker build -t i18n-l10n-app .
```

### Run the container

```bash
docker run -p 8080:8080 \
  -e GOOGLE_CLIENT_ID=your_client_id \
  -e GOOGLE_CLIENT_SECRET=your_client_secret \
  -e JWT_SECRET=your_jwt_secret \
  i18n-l10n-app
```

The application will be available at `http://localhost:8080/login`

## Project Structure

```
i18n_l10n/
├── i18n_l10n/              # Main application package
│   ├── __init__.py
│   ├── main.py             # Main application code
│   ├── auth.py             # Google OAuth authentication
│   ├── database.py         # Database models and operations
│   └── admin/              # Admin interface
│       └── page.py         # Admin page components
├── deploy/                 # Deployment configurations
│   ├── terraform/          # Infrastructure as Code
│   └── *.yaml              # Cloud deployment configs
├── scripts/                # Utility scripts
│   ├── setup_google_oauth.sh
│   └── deploy_with_auth.sh
├── alembic/                # Database migrations
├── pyproject.toml          # Poetry configuration
├── requirements.txt        # pip requirements for Docker
├── Dockerfile             # Docker configuration
├── test_auth.py           # Authentication testing
├── GOOGLE_OAUTH_SETUP.md  # OAuth setup guide
└── README.md              # This file
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

## API Endpoints

### Authentication
- `GET /login` - Login page with Google OAuth
- `POST /api/auth/google` - OAuth callback endpoint
- `GET /logout` - Logout page

### Translation Management
- `GET /admin` - Admin interface (requires authentication)
- `POST /api/translate` - Translation API endpoint

### Translation API Usage

```bash
curl -X POST http://localhost:8080/api/translate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello World",
    "src": "en-US",
    "dst": "es-ES",
    "context": "greeting",
    "key": "hello_world"
  }'
```

## Authentication Flow

1. User visits `/login`
2. Clicks "Sign in with Google"
3. Completes Google OAuth flow
4. Receives JWT token
5. Redirected to `/admin` with authentication
6. Token stored in localStorage for subsequent requests

## Security Features

- Google OAuth 2.0 authentication
- JWT token-based sessions
- HTTPS enforcement in production
- Environment variable configuration
- Secure token storage

## Future Enhancements

- [ ] Role-based access control
- [ ] Translation workflow management
- [ ] Bulk translation operations
- [ ] Translation quality metrics
- [ ] Multi-tenant support
- [ ] Advanced search and filtering

## License

This project is open source and available under the MIT License.

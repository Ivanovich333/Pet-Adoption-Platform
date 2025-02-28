# Pet Adoption Platform

A Django-based web application for pet adoption management.

## Project Setup

This project uses Poetry for dependency management:

```bash
# Install dependencies
poetry install

# Activate the virtual environment
poetry shell
```

## Getting Started

To run the development server:

```bash
python manage.py runserver
```

## Docker Setup

This project includes Docker configuration for easy setup and deployment.

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Local Development with Docker

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd pet-adoption
   ```

2. Create a `.env` file from the example:
   ```bash
   cp .env.example .env
   ```
   
   Edit the `.env` file and update the values as needed.

3. Build and run the containers:
   ```bash
   docker-compose up --build
   ```

4. Access the application at http://localhost:8000

### Docker Commands

```bash
# Start the services in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the services
docker-compose down

# Remove volumes along with containers
docker-compose down -v

# Run management commands
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

## Production Deployment

For production deployment, update the `.env` file with appropriate settings:

- Set `DEBUG=False`
- Generate a new `SECRET_KEY`
- Update `ALLOWED_HOSTS` with your domain
- Configure email settings
- Set up a proper database password

Then rebuild and restart the containers:

```bash
docker-compose build
docker-compose up -d
``` 
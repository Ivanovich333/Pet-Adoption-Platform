# GitHub Actions CI/CD Setup Instructions

This document provides instructions on setting up secrets required for the CI/CD pipeline.

## Required Secrets

You need to add these secrets to your GitHub repository for the CI/CD pipeline to work properly:

1. `DOCKER_HUB_USERNAME`: Your Docker Hub username
2. `DOCKER_HUB_ACCESS_TOKEN`: Your Docker Hub access token (not your password)

For deployment, you will also need (once enabled in the workflow):
1. `SERVER_HOST`: The host/IP address of your server
2. `SERVER_USERNAME`: SSH username for your server
3. `SERVER_SSH_KEY`: SSH private key for authentication

## Setting Up Secrets in GitHub

1. Go to your repository on GitHub
2. Click on "Settings" tab
3. In the left sidebar, click on "Secrets and variables" → "Actions"
4. Click "New repository secret"
5. Add each secret with its appropriate value

## Creating a Docker Hub Access Token

1. Log in to [Docker Hub](https://hub.docker.com/)
2. Click on your username and go to "Account Settings"
3. Go to "Security" section
4. Click "New Access Token"
5. Give it a name (e.g., "GitHub Actions") and set appropriate permissions
6. Copy the token immediately (it will only be shown once)
7. Add this token as the `DOCKER_HUB_ACCESS_TOKEN` secret in GitHub

## Setting Up SSH Keys for Deployment

1. Generate a new SSH key pair (if you don't have one):
   ```bash
   ssh-keygen -t ed25519 -f github-actions-deploy -C "github-actions-deploy"
   ```
2. Add the public key (github-actions-deploy.pub) to the authorized_keys file on your server
3. Add the private key (github-actions-deploy) content as the `SERVER_SSH_KEY` secret in GitHub

## Enabling Deployment

The deployment job is commented out by default in the workflow. Once you've set up all required secrets, you can uncomment the deployment section in `.github/workflows/django-ci.yml`. 
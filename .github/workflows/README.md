# GitHub Actions CI Workflows

This directory contains the CI/CD pipeline configurations for MedBot Intelligence.

## ci.yml

The `ci.yml` workflow triggers on pushes and pull requests to the `main` branch. It consists of three main jobs:

1.  **Frontend Build (`frontend-build`)**:
    -   Installs Node.js dependencies.
    -   Runs linting (`npm run lint`).
    -   Builds the Next.js application.

2.  **Backend Services (`backend-services-test`)**:
    -   Runs in parallel for each microservice defined in the matrix.
    -   Installs Python dependencies.
    -   Runs `flake8` for linting.
    -   Runs `pytest` if tests are found in the service directory.

3.  **Eureka Server (`eureka-server-build`)**:
    -   Builds the Java-based Eureka Server using Maven.

## Usage

To enable this pipeline, simply push the `.github` folder to your GitHub repository. The actions will automatically start running.

## Adding Tests

To ensure your services are tested, add `pytest` compatible tests in a `tests/` folder within each service directory (e.g., `services/api-gateway/tests/`).

## SecRuleEngine+ Demo Project Deployment and Running Guide

Congratulations on successfully running your application inside Docker! This guide will help you or anyone else set up and run your project from scratch in a new environment.

### 1. Prerequisites

Before you begin, make sure your system meets the following prerequisites:

- **Operating System**: Ubuntu 20.04 or later
- **Git**: Git installed (for cloning the project)

### 2. Project Setup Steps

#### 2.1 Clone the Project

First, clone your project to your local environment:

```bash
git clone <your-project-Git-URL>
cd <your-project-directory>
```

#### 2.2 Run `setup.sh`

Inside the project directory, there is a `setup.sh` script. This script will automatically install all necessary dependencies and set up Docker, Docker Compose, and Python environments.

Run the following commands to execute the `setup.sh` script:

```bash
chmod +x setup.sh
./setup.sh
```

##### What `setup.sh` Does

- **On the Host Machine**:
  - Installs `python3-apt` for managing Python packages via apt.
  - Installs Docker components (`docker-ce`, `docker-ce-cli`, `containerd.io`, `docker-compose-plugin`) for containerization.
  - Installs Python 3.10 and sets it as the default Python version.
  - Installs Docker Compose for multi-container Docker applications.

- **In the Virtual Environment**:
  - Creates a Python virtual environment (`.venv`).
  - Installs `pip` for managing Python packages.
  - Installs `setuptools` to easily download, build, install, upgrade, and uninstall Python packages.
  - Installs `Cython` to allow C extensions for Python.
  - Installs `PyYAML` for YAML parsing.

> **Note**: During the script execution, you may need to enter your administrator password to install necessary packages.

#### 2.3 Set Up Environment Variables

Ensure that your `.env` file is correctly configured with the required environment variables. The `.env` file should be in the project directory. An example entry might be:

```bash
API_KEY=xxxx
```

Make sure to replace `xxxx` with your actual API key or relevant environment-specific variables.

#### 2.4 Build and Run Docker Containers

Use Docker Compose to build and run the project containers:

```bash
docker-compose up --build
```

This command will:

- Build your frontend and backend Docker images based on the configuration in the `docker-compose.yml` file.
- Start the Docker containers and map the corresponding ports.

##### Troubleshooting Build and Run Issues

If you encounter issues during this step, here are some commands and tips to help diagnose and solve common problems:

1. **Ensure Docker Daemon is Running**:  
   The Docker daemon must be running to use Docker commands. To check if Docker is running, use:

   ```bash
   sudo service docker status
   ```

   If it is not running, start the Docker service with:

   ```bash
   sudo service docker start
   ```

   If your system uses `systemd`, you might need to start Docker with:

   ```bash
   sudo systemctl start docker
   ```

2. **Check Docker Logs**: If there is an error, check the logs for more details:

   ```bash
   docker-compose logs
   ```

3. **Restart Docker**: Sometimes, restarting Docker can resolve unexpected issues:

   ```bash
   sudo systemctl restart docker
   ```

4. **Rebuild Images Without Cache**: If you encounter build errors, try rebuilding the images without using cache:

   ```bash
   docker-compose build --no-cache
   docker-compose up
   ```

5. **Ensure `.env` File is Loaded**: Verify that Docker Compose is loading the `.env` file by running:

   ```bash
   docker-compose config
   ```

   This command will display the configuration after environment variables are loaded.

6. **Remove and Recreate Containers**: If you have persistent issues, remove the containers and start fresh:

   ```bash
   docker-compose down
   docker-compose up --build
   ```

#### 2.5 Verify Running Status

To check if the application is running successfully, open the following URLs in your browser to access the frontend and backend services:

- Frontend: [http://localhost:3000](http://localhost:3000)
- Backend API: [http://localhost:8080/docs](http://localhost:8080/docs)

These pages should display your application interface and API documentation.

### 3. Stop Docker Containers

If you need to stop the running Docker containers, you can use the following command:

```bash
docker-compose down
```

This command will stop and remove all containers related to the `docker-compose.yml` definition.

### 4. Update and Redeploy

If you need to update the application code or configuration, make the necessary changes, then rebuild and restart the containers:

```bash
docker-compose up --build
```

This will rebuild the images and restart the containers.

## Contact

👨🏻‍💻 **Author**: Jerry Hung, Dickson Chiou, Bolt Lin from iii-csti  
📮 **Email**: [jerryhung@iii.org.tw](mailto:jerryhung@iii.org.tw)
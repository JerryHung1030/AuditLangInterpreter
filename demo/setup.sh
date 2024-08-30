#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Function to display a banner at the start
display_banner() {
    echo "============================================================================"
    echo "                          Security Audit Platform Setup                     "
    echo "============================================================================"
    echo "This script will set up all necessary dependencies and configurations to run"
    echo "the Security Audit Platform on Ubuntu 20.04 or higher. Please ensure you have"
    echo "sudo privileges before running this script."
    echo ""
    echo "The following software will be installed on your system:"
    echo "  - On the host machine:"
    echo "      - python3-apt"
    echo "      - Docker (docker-ce, docker-ce-cli, containerd.io, docker-compose-plugin)"
    echo "      - Python 3.10"
    echo "      - Docker Compose"
    echo "  - In the virtual environment (.venv):"
    echo "      - pip"
    echo "      - setuptools"
    echo "      - Cython"
    echo "      - PyYAML"
    echo "============================================================================"
    echo ""
}

# Function to display section headers
display_section() {
    echo ""
    echo "----------------------------------------------------------------------------"
    echo "$1"
    echo "----------------------------------------------------------------------------"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if Python 3.10 is already the default Python3 version
is_python3_10_default() {
    python3 --version 2>&1 | grep -q "3.10"
}

# Function to check if the script is running on Ubuntu 20.04 or higher
check_ubuntu_version() {
    display_section "Checking Ubuntu Version"
    . /etc/os-release
    if [[ "$NAME" == "Ubuntu" ]] && [[ "${VERSION_ID}" < "20.04" ]]; then
        echo "ERROR: This script requires Ubuntu 20.04 or higher. You are running $VERSION_ID."
        exit 1
    fi
    echo "Ubuntu version is $VERSION_ID. Compatible version detected, continuing setup..."
}

# Function to prompt user for continuation
prompt_user() {
    echo ""
    read -p "Do you want to proceed with the installation? (yes/no): " choice
    case "$choice" in 
        yes|Yes|YES) 
            echo "Proceeding with installation..."
            ;;
        no|No|NO) 
            echo "Installation aborted by user."
            exit 0
            ;;
        *) 
            echo "Invalid input. Please type 'yes' or 'no'."
            prompt_user
            ;;
    esac
}

# Display the banner
display_banner

# Prompt user for continuation
prompt_user

# Check Ubuntu version
check_ubuntu_version

# Ensure python3-apt is properly installed
display_section "Checking Python3-APT Installation"
if ! dpkg -l | grep -q python3-apt; then
    echo "Installing python3-apt..."
    sudo apt-get update
    sudo apt-get install -y python3-apt
else
    echo "python3-apt is already installed. Reinstalling to ensure functionality..."
    sudo apt-get install --reinstall -y python3-apt
fi

# Enable the universe repository to access all packages
display_section "Enabling Universe Repository"
sudo add-apt-repository universe || echo "Warning: Couldn't enable universe repository. Please check your system configuration."
sudo apt-get update

# Install prerequisite packages if they are not installed
display_section "Installing Prerequisite Packages"
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    software-properties-common \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    python3.10-venv \
    python3-distutils \
    python3-lib2to3 \
    python3.10-dev

# Check for Docker installation
display_section "Checking Docker Installation"
if command_exists docker; then
    echo "Docker is already installed."
else
    echo "Installing Docker..."
    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
    $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    echo "Docker installation complete."
fi

# Add current user to the Docker group
display_section "Adding User to Docker Group"
if groups $USER | grep &>/dev/null '\bdocker\b'; then
    echo "User is already in the Docker group."
else
    echo "Adding user to the Docker group..."
    sudo usermod -aG docker $USER
    echo "User added to the Docker group."
fi

# Check if Python 3.10 is already installed
display_section "Checking Python 3.10 Installation"
if python3.10 --version &>/dev/null; then
    echo "Python 3.10 is already installed."
else
    echo "Installing Python 3.10..."
    sudo add-apt-repository ppa:deadsnakes/ppa -y
    sudo apt-get update
    sudo apt-get install -y python3.10 python3.10-venv python3.10-dev
    echo "Python 3.10 installation complete."
fi

# Install distutils for Python 3.10 using apt-get
display_section "Installing Python 3.10 Distutils"
if ! dpkg -l | grep -q python3.10-distutils; then
    echo "Installing distutils for Python 3.10..."
    sudo apt-get install -y python3-distutils python3-lib2to3
else
    echo "distutils for Python 3.10 is already installed."
fi

# Set Python 3.10 as the default Python version if it is not already set
display_section "Setting Python 3.10 as Default"
if is_python3_10_default; then
    echo "Python 3.10 is already set as the default."
else
    echo "Setting Python 3.10 as the default Python version..."
    sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1
    echo "Python 3.10 is now the default Python version."
fi

# Create a virtual environment if it doesn't exist
VENV_DIR=".venv"
display_section "Creating Virtual Environment"
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating a virtual environment in $VENV_DIR..."
    python3.10 -m venv $VENV_DIR
fi

# Activate the virtual environment
display_section "Activating Virtual Environment"
source $VENV_DIR/bin/activate

# Ensure pip is installed in the virtual environment
display_section "Ensuring Pip Installation"
if ! $VENV_DIR/bin/python -m pip --version &> /dev/null; then
    echo "Installing pip in the virtual environment..."
    curl -sS https://bootstrap.pypa.io/get-pip.py | $VENV_DIR/bin/python
fi

# Install setuptools for Python 3.10 in the virtual environment if not already installed
display_section "Installing Setuptools"
if ! $VENV_DIR/bin/python -m pip show setuptools &>/dev/null; then
    echo "Installing setuptools for Python 3.10..."
    $VENV_DIR/bin/python -m pip install setuptools
else
    echo "setuptools for Python 3.10 is already installed."
fi

# Upgrade pip to ensure compatibility with PyYAML installation
display_section "Upgrading Pip"
$VENV_DIR/bin/python -m pip install --upgrade pip

# Install Cython in the virtual environment using pip (since apt version isn't available)
display_section "Installing Cython"
$VENV_DIR/bin/python -m pip install cython

# Install PyYAML separately to avoid build issues
display_section "Installing PyYAML"
$VENV_DIR/bin/python -m pip install --no-binary :all: PyYAML

# Install Docker Compose directly without using pip
display_section "Installing Docker Compose Directly"
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Check installations
display_section "Checking Installations"
echo "Docker Version:"
docker --version

echo "Docker Compose Version:"
docker-compose --version

echo "Python Version:"
python3 --version

echo "Setup complete! Please restart your terminal or run 'newgrp docker' to apply Docker group changes."

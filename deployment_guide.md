# Deployment Guide for Oracle VPS

## 1. Connect to your VPS
You already know how to do this:
```bash
ssh -i id_ed25519 ubuntu@129.154.227.67
```

## 2. Update System and Install Dependencies
Run the following commands on your Ubuntu VPS to ensure it's up to date:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git curl ufw
```

## 3. Install Docker and Docker Compose
Install Docker engine and the Compose plugin:
```bash
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

# Install Docker packages
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Allow your user to run docker commands without sudo
sudo usermod -aG docker $USER
# NOTE: You will need to log out and log back in (or run `newgrp docker`) for this to take effect.
```

## 4. Configure UFW (Ubuntu Firewall)
You mentioned you opened ports on the Oracle Cloud Security List. You also need to allow them through Ubuntu's internal firewall (UFW):
```bash
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8000/tcp  # Optional, if you want direct access to the backend API

# Enable UFW
sudo ufw enable
# Type 'y' when it asks if you want to proceed with disrupting existing ssh connections
```

## 5. Clone the Repository
Clone your project repository onto the VPS:
```bash
git clone <your-github-repo-url> digital-twin
cd digital-twin
```

## 6. Setup Environment Variables
Before running the containers, ensure your `.env` file is present in the `digital-twin` root directory on the VPS (the same one you have locally, with API keys). **Do not commit API keys to version control.** Copy your local `.env` file to the server.
```bash
# You can use nano to paste your .env contents
nano .env
```

## 7. Start the Application
Use Docker Compose to build and start the application in detached mode:
```bash
docker compose up -d --build
```

**What this does:**
1. It builds the Python backend container, installing all dependencies from `requirements.txt`.
2. It builds the Node.js frontend container, executing `npm run build` inside, and then serving the static files via Nginx.
3. Nginx is configured to serve the frontend on port 80 and proxy any `/requirements`, `/design`, `/simulation`, `/export`, and `/codegen` requests directly to the backend container (port 8000).

## 8. Verify the Deployment
Once the containers are running:
- Open your browser and go to `http://129.154.227.67`. You should see the frontend.
- Check if the containers are healthy:
  ```bash
  docker ps
  ```
- View logs if something goes wrong:
  ```bash
  docker compose logs -f
  ```

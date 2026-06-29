# CI/CD Setup Guide - GitHub Actions

## Overview
This guide explains how to set up Continuous Integration/Continuous Deployment (CI/CD) for your Height Prediction API.

---

## What Each Step Does

### ✅ **Job 1: Test (Runs First)**
- Checks out your code
- Sets up Python 3.11
- Installs dependencies
- Runs tests to verify everything works
- **Status**: If this fails, the pipeline stops ❌

### 🐳 **Job 2: Build Docker Image (Runs After Test Passes)**
- Builds your Docker image
- Pushes it to Docker Hub
- Tags it with `latest` and the commit SHA
- **Status**: Only runs if test passes ✅

### 🚀 **Job 3: Deploy (Optional)**
- Notifies you that the image is ready
- You can customize this to auto-deploy to cloud

---

## Setup Instructions

### **Step 1: Push Code to GitHub**

```bash
cd d:\Learning_python\projects\simpleLinearRegression
git init
git add .
git commit -m "Add CI/CD pipeline"
git remote add origin https://github.com/YOUR_USERNAME/height-prediction.git
git branch -M main
git push -u origin main
```

### **Step 2: Create Docker Hub Account**
1. Go to https://hub.docker.com
2. Sign up (free)
3. Create a repository named `height-prediction`

### **Step 3: Add GitHub Secrets**

GitHub Secrets are secure environment variables. They're used so your credentials aren't exposed in the code.

**Steps:**
1. Go to your GitHub repo → **Settings** tab
2. Click **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add these two secrets:

| Secret Name | Value |
|------------|-------|
| `DOCKER_USERNAME` | Your Docker Hub username |
| `DOCKER_PASSWORD` | Your Docker Hub password/token |

**⚠️ Important**: Your credentials are encrypted and secure. GitHub doesn't show them publicly.

### **Step 4: Test the Pipeline**

```bash
git add .
git commit -m "Add initial test"
git push origin main
```

**Check the results:**
1. Go to your GitHub repo
2. Click **Actions** tab
3. Watch the workflow run in real-time
4. Click on the workflow to see detailed logs

---

## Understanding the Workflow File (.github/workflows/deploy.yml)

### **Triggers** (When does it run?)
```yaml
on:
  push:
    branches:
      - main          # Runs when code is pushed to main
  pull_request:
    branches:
      - main          # Also runs on pull requests
```

### **Jobs** (What tasks run?)
```yaml
jobs:
  test:              # First job: run tests
  build:             # Second job: build Docker image
  deploy:            # Third job: deploy (notification for now)
```

### **Dependencies** (What runs after what?)
```yaml
needs: test          # This job waits for 'test' job to pass
```

### **Secrets** (Secure credentials)
```yaml
${{ secrets.DOCKER_USERNAME }}    # Accesses the secret safely
```

---

## What Happens Next (After Deployment)

### **Option 1: Manual Deployment (You control when to deploy)**
- Image is built and pushed to Docker Hub ✅
- You manually pull and deploy when ready

### **Option 2: Auto-Deploy (If you want automatic deployment)**
You can customize the `deploy` job to automatically deploy to:
- **Heroku**: `git push heroku main`
- **AWS**: Use AWS CLI to update ECS service
- **Google Cloud Run**: Use gcloud CLI
- **DigitalOcean**: Use their CLI

---

## Common Commands to Know

| Command | What it does |
|---------|-------------|
| `git push origin main` | Push changes and trigger CI/CD |
| `git pull origin main` | Get latest changes |
| `git log` | See commit history |
| `docker pull USERNAME/height-prediction:latest` | Pull your image from Docker Hub |

---

## Troubleshooting

### ❌ Pipeline fails at "Login to Docker Hub"
- Check if `DOCKER_USERNAME` and `DOCKER_PASSWORD` secrets are set correctly
- Make sure your Docker Hub credentials are correct

### ❌ Tests fail
- Check the log for error details
- Fix the code locally first
- Commit and push again

### ✅ Pipeline passes but no image on Docker Hub
- Go to Docker Hub and check your repository
- Wait a few seconds; it might still be uploading
- Refresh the page

---

## Next Steps After This Works

1. **Add More Tests**: Write proper unit tests in `tests/` folder
2. **Add Code Quality Checks**: Use tools like `black`, `flake8`, `pylint`
3. **Add Security Scanning**: Scan for vulnerabilities
4. **Deploy Automatically**: Set up auto-deployment to cloud platform
5. **Add Monitoring**: Monitor your deployed application

---

## Learning Resources

- **GitHub Actions Docs**: https://docs.github.com/en/actions
- **Docker Hub**: https://hub.docker.com
- **FastAPI**: https://fastapi.tiangolo.com/

---

## Example: Complete Flow

```
You push code to GitHub (git push)
    ↓
GitHub Actions triggers automatically
    ↓
Job 1: Test your code ✅
    ↓
Job 2: Build Docker image 🐳
    ↓
Job 3: Notify you it's ready 🚀
    ↓
Your Docker image is on Docker Hub ready to deploy!
```


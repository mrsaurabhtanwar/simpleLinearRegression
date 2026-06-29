# GitHub Actions Workflow - Detailed Breakdown

## File Location
`.github/workflows/deploy.yml`

This is the configuration file that tells GitHub how to run your CI/CD pipeline.

---

## Line-by-Line Explanation

### 1. **Workflow Name**
```yaml
name: CI/CD Pipeline
```
- This is the name shown in GitHub's Actions tab
- Makes it easy to identify your workflow

---

### 2. **Triggers** (When does the workflow run?)
```yaml
on:
  push:
    branches:
      - main          # Run when code is pushed to 'main' branch
  pull_request:
    branches:
      - main          # Also run when someone creates a pull request to 'main'
```

**Why two triggers?**
- `push`: Runs when you push code
- `pull_request`: Runs when someone wants to merge changes (lets you review before merging)

---

### 3. **Jobs Definition**
```yaml
jobs:
  test:              # First job: runs tests
  build:             # Second job: builds Docker image
  deploy:            # Third job: deployment notification
```

---

## Job 1: TEST

```yaml
test:
  runs-on: ubuntu-latest  # Run on a GitHub-provided Linux machine
  
  steps:
    - name: Checkout code
      uses: actions/checkout@v3
      # Clones your repository into the runner machine
      
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
      # Installs Python 3.11
      
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest
      # Installs your app dependencies + pytest for testing
      
    - name: Run tests
      run: |
        python -c "import fastapi; import joblib; import mysql.connector; print('All imports successful!')"
      # Runs a simple test to verify all imports work
      # You can replace this with: pytest tests/
```

**What happens if this job fails?**
- ❌ The pipeline stops
- Build and Deploy jobs don't run
- You get notified

---

## Job 2: BUILD & PUSH DOCKER

```yaml
build:
  needs: test  # This job only runs if 'test' job passes ✅
  runs-on: ubuntu-latest
  
  # This condition means: only run on main branch, only on push (not pull requests)
  if: github.ref == 'refs/heads/main' && github.event_name == 'push'
  
  steps:
    - name: Checkout code
      uses: actions/checkout@v3
      # Get your code again
```

**Why `needs: test`?**
- Ensures tests pass before building
- Prevents pushing broken Docker images

```yaml
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
      # Prepares Docker for building
```

**What is Docker Buildx?**
- A tool that builds Docker images efficiently
- Supports caching (faster rebuilds)

```yaml
    - name: Login to Docker Hub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}
      # Logs into Docker Hub using your secrets
```

**Why secrets?**
- Never hardcode credentials in code
- `${{ secrets.DOCKER_USERNAME }}` safely accesses them

```yaml
    - name: Build and push Docker image
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: |
          ${{ secrets.DOCKER_USERNAME }}/height-prediction:latest
          ${{ secrets.DOCKER_USERNAME }}/height-prediction:${{ github.sha }}
        cache-from: type=registry,ref=${{ secrets.DOCKER_USERNAME }}/height-prediction:buildcache
        cache-to: type=registry,ref=${{ secrets.DOCKER_USERNAME }}/height-prediction:buildcache,mode=max
```

**What does this do?**
- Builds Docker image from Dockerfile
- Tags with two versions:
  - `:latest` - always points to the newest version
  - `:SHA` - specific commit (e.g., `abc12345` - never changes)
- Uses caching to speed up builds
- Pushes to Docker Hub

**Example result on Docker Hub:**
```
height-prediction:latest      (newest)
height-prediction:abc12345    (specific commit)
height-prediction:def67890    (older commit)
```

---

## Job 3: DEPLOY

```yaml
deploy:
  needs: build  # Only runs if 'build' job passes
  runs-on: ubuntu-latest
  if: github.ref == 'refs/heads/main' && github.event_name == 'push'
  
  steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Deploy notification
      run: |
        echo "✅ Docker image built and pushed successfully!"
        echo "🚀 Ready to deploy to production"
        echo "Next steps:"
        echo "1. Go to your cloud provider"
        echo "2. Deploy the image: username/height-prediction:SHA"
        echo "3. Set environment variables"
```

**What does this do?**
- Currently just prints a message
- Can be customized to auto-deploy to cloud providers
- Good place to add Slack/email notifications

---

## How Context Variables Work

| Variable | Value | Example |
|----------|-------|---------|
| `${{ secrets.DOCKER_USERNAME }}` | Your Docker username (secret) | `myusername` |
| `${{ github.sha }}` | Current commit ID | `abc12345678` |
| `${{ github.ref }}` | Branch name | `refs/heads/main` |
| `${{ github.event_name }}` | Trigger type | `push` or `pull_request` |

---

## Full Pipeline Flow (Visual)

```
Developer: git push origin main
    ↓
GitHub: "A push to main! Triggering workflow!"
    ↓
Runner 1: "Running TEST job..."
├─ Checkout code ✅
├─ Setup Python ✅
├─ Install dependencies ✅
├─ Run tests ✅
└─ Result: SUCCESS ✅
    ↓
Runner 2: "TEST passed, running BUILD job..."
├─ Checkout code ✅
├─ Setup Docker ✅
├─ Login to Docker Hub ✅
├─ Build image ✅
├─ Push to Docker Hub ✅
└─ Result: SUCCESS ✅
    ↓
Runner 3: "BUILD passed, running DEPLOY job..."
├─ Notify deployment ready ✅
└─ Result: SUCCESS ✅
    ↓
GitHub: "✅ All jobs passed!"
Docker Hub: "🐳 New image: username/height-prediction:latest"
```

---

## Common Customizations

### Run Pytest for Real Tests
```yaml
    - name: Run tests
      run: pytest tests/ -v
```

### Deploy to Heroku Automatically
```yaml
    - name: Deploy to Heroku
      run: |
        git remote add heroku https://git.heroku.com/your-app.git
        git push heroku main
```

### Add Slack Notification on Failure
```yaml
    - name: Notify Slack on failure
      if: failure()
      uses: slackapi/slack-github-action@v1.24.0
      with:
        webhook-url: ${{ secrets.SLACK_WEBHOOK }}
```

### Schedule Pipeline to Run Daily
```yaml
on:
  schedule:
    - cron: '0 0 * * *'  # Run at midnight UTC daily
```

---

## Troubleshooting

### "Failed to login to Docker Hub"
- Check if `DOCKER_USERNAME` and `DOCKER_PASSWORD` secrets are set
- Use a Personal Access Token instead of password (more secure)

### "Tests are failing in GitHub but pass locally"
- Environment differences (Python version, missing files, etc.)
- Check the detailed logs in GitHub Actions
- Test locally exactly like GitHub does: `python -c "import module"`

### "Build is slow"
- GitHub runners can be slower than your local machine
- Use Docker layer caching (already in the workflow)
- Optimize your Dockerfile to reduce dependencies

---

## Next Level: Advanced Customizations

1. **Matrix Strategy** - Test on multiple Python versions
2. **Workflow Status Badges** - Show build status in README
3. **Scheduled Runs** - Run tests on a schedule
4. **Artifacts** - Save test reports, coverage reports
5. **Release Management** - Auto-create releases on tags

---

**Happy learning! 🚀**

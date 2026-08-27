// start service cmd
/venv/bin/python -m uvicorn app.main:app --reload --port 8001



<!-- BUild image -->
docker build --no-cache -t namankali/devops-py-service:latest .
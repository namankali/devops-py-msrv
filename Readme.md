// start service cmd
/venv/bin/python -m uvicorn app.main:app --reload --port 8001



<!-- BUild image -->
docker build -t namankali/devops-py-service:latest .
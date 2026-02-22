.PHONY: backend docker ios clean help

help:
	@echo "Targets:"
	@echo "  backend  - Run FastAPI locally with venv"
	@echo "  docker   - Run backend via docker compose"
	@echo "  ios      - Generate and open Xcode project"
	@echo "  clean    - Remove backend venv"

backend:
	bash backend/run.sh

docker:
	cd backend && cp -n .env.example .env 2>/dev/null || true && docker compose up --build -d
	@echo "Backend is starting in Docker. Visit http://localhost:8000/health"

ios:
	bash ios/bootstrap.sh

clean:
	rm -rf backend/.venv

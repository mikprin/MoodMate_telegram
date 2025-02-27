help:
	@echo "Available targets:"
	@echo "  help   - Show this help message"
	@echo "  test   - Run pytest test suite"
	@echo "  up     - Start containers with Docker Compose"

# Test with python3 -m pytest test/tests/
.PHONY: test
test:
	export SQLITE_DB_PATH=./test_db.db && python3 -m pytest -vv test/tests/

up:
	docker compose up -d --build


.PHONY: down
down:
	docker compose stop && docker compose down

.PHONY: backup
backup:
	./scripts/backup.sh

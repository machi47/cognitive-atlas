.PHONY: install dev test build run migrate smoke push backup

install:
	./scripts/install.sh

dev:
	./scripts/dev.sh

test:
	./scripts/test.sh

build:
	./scripts/build.sh

run:
	./scripts/run_api.sh

migrate:
	./scripts/migrate.sh

smoke:
	./scripts/smoke_test.sh

push:
	./scripts/create_github_repo.sh

backup:
	./scripts/backup.sh

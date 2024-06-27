.PHONY: run create-migrations run-migrations

run:
	@uvicorn workout_api.main:app --reload

create-migrations:
	@alembic revision --autogenerate -m "$(d)"

run-migrations:
	@alembic upgrade head
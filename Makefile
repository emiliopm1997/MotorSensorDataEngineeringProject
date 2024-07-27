beautify:
	python -m isort credentials_validator
	python -m isort data_handler
	python -m isort orchestrator
	python -m isort processors
	python -m isort stream_generator

	python -m black --line-length 80 credentials_validator
	python -m black --line-length 80 data_handler
	python -m black --line-length 80 orchestrator
	python -m black --line-length 80 processors
	python -m black --line-length 80 stream_generator

start:
	docker-compose up -d --build
	docker exec -it orchestrator_container curl http://orchestrator:5000/start_pipeline

test:
	python -m unittest discover -v ./stream_generator
	python -m unittest discover -v ./data_handler
	python -m unittest discover -v ./processors
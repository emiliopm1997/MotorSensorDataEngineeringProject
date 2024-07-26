start:
	docker-compose up -d --build
	docker exec -it orchestrator_container curl http://orchestrator:5000/start_pipeline

test:
	python -m unittest discover -v ./stream_generator
	python -m unittest discover -v ./data_handler
	python -m unittest discover -v ./processors
start:
	docker-compose up --build

test:
	python -m unittest discover -v ./stream_generator
	python -m unittest discover -v ./data_handler
	python -m unittest discover -v ./preprocessors
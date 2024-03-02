start:
	docker-compose up --build

test:
	python -m unittest discover -v ./stream_generator
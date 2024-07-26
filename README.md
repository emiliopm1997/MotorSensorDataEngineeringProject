# MotorSensorDataEngineeringProject
This project is for a master's degree course in data engineering. It simulates the voltage data of a medium motor and its path through different objects and modules, all the way to a reporting microservice.

Things that can be improved:
- Credentials validator is overly simplistic
- Raw data validations
- API unittests
- Improve API codes
- Generalize data base modules for multiple signals

Notes:

Start services
docker compose up -d --build

Shut down services
docker compose down

Check running containers
docker ps

Inspect network
docker network inspect <network_name>

Remove network
docker network rm <network_name>    

Stop container
docker stop <container_name>

Build individual image
docker build -t <image_name> <dockerfile_path>

Run image in container
docker run -it --network=<network_name> --name <container_name> <image_name>

docker exec -it orchestrator_container curl http://orchestrator:5000/start_pipeline
curl http://data_handler:5002/save_raw_data
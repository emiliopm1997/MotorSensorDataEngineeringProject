# MotorSensorDataEngineeringProject
This project is for a master's degree course in data engineering. It simulates the voltage data of a medium motor and its path through different objects and modules, all the way to a reporting microservice.


Notes:

Start services
docker compose up -d

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

docker build -t stream_generator ./stream_generator
docker run -it --network=motor_sensor_network --name sg_container stream_generator
telnet localhost 9093
curl http://127.0.0.1:5001/start_generating_values

docker run --rm -v $PWD/data/kafka:/var/lib/kafka/data confluentinc/cp-kafka:latest kafka-storage.sh format -t "kafka-cluster" -c /etc/kafka/kraft/server.properties

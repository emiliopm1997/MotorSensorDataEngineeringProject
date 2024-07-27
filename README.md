# Motor Sensor Data Engineering Project

## General description

This project is for a master's degree course in data engineering. It simulates the voltage data of a medium motor and its path through different microservices that save and process the data until it can be fed to a dashboard to check for anomalies. The voltage of the motor has a base value and significantly increases when the motor recieves a load; therefore, if the voltage as a function of time was to be plotted, we would see a periodical function with some noise.

Each component has its own Dockerfile and yaml file, so their containers are independent from each other, and simulate microservices. Also, each component contains at least one log file to monitor the requests and actions of each, and to facilitate debugging when an unexpected outcome is encountered. Furthermore, there are unit tests that cover most of the functionalities of each microservice; nevertheless, they focus mainly in the internal modules of the component opposed to the API functionality of each.

There are 5 components (6 if one considers the imported Kafka server) within this project. The "orchestrator" component is in charge of starting the main pipline, and contains an example file ("retrieving_example.py") which can be used as a guideline once a dynamic dashboard tool has been set for plotting the voltage signals and the different metrics calculated for the load cycles. Next, the "stream generator" is responsible of simulating the voltage previously described, and create a stream using Kafka. Moreover, the "credentials validator" is a component used to validate that the user has permission to read and write on the data bases; however, it is worth noting that this component is overly simplified given that it wasn't as relevant for the scope of the project and, therefore, should definitely be improved for a production environment. Notably, the project also contains the "data handler" microservice that is in charge of reading the Kafka stream, saving the raw stream data into a data lake, processing the data from the data lake (through the "processors" microservice), saving this processed data into a data warehouse, and retriving both raw and processed data that is within two time periods. As one would expect, these tasks are separated by three different end points. Additionally, one can access the data bases thanks to a volume connection. Finally, the "processors" microservice is responsible of cutting the load cycles and calculating different metrics for every one of them (each functionality is an end point).

## How to run.

All these microservices have specific requirements and must be connected to the same network to be able to work seamlessly. Therefore, I created a "docker-compose" file to facilitate the running of this project. To do so, one must follow these steps:

1. Build and start the microservices by running: `docker compose up -d --build`.
2. Ensure that the 6 microservices are up with: `docker ps`.
3. Start the pipline through the "orchestrator" by running: `docker exec -it orchestrator_container curl http://orchestrator:5000/start_pipeline`.
4. Check the response message, logs, and data bases.
5. (Optional) If one desires to simulate the retrieval of data for a dashboard, one can run: `docker exec -it orchestrator_container python retrieving_example.py`. If successful, the components will be printed.
6. To close the services, run: `docker compose down`.

## Cautions

There are a couple of items one must be aware of when deleting logs and data bases:

- Logs should be deleted when the services are down.
- Data bases should be deleted when the services are up but the pipeline hasn't started.

Doing otherwise can cause errors that might require the user to enter the container and delete the files manually.

Also, note the dev container found in this project is only for development purposes; thus, the services are not designed to be run inside it.

## Items to improve:

- Credentials validator: increse complexity to improve data security and compliance.
- Raw data validations: create a microservice that is called before writing the raw data that ensure the data from the stream contains the expected format and values.
- API unit tests: test the different scenarios that each API can have.
- Improve API response codes: catch more errors and follow more API best practices.
- Generalize data base modules: generalize it for multiple signals that can come from motors or other components inside a factory. Consider that the quantities to measure are not always voltages.

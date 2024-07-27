# Base image for the container
FROM continuumio/miniconda3

WORKDIR /src

# Install curl for requests
RUN apt-get update && apt-get install curl -y

# Install mamba
RUN conda install -c conda-forge mamba

# Setup basic conda environment
ENV CONDA_ENVIRONMENT cred_validator_env
COPY environment.yml .

RUN mamba env create --file environment.yml && \
    echo "source activate ${CONDA_ENVIRONMENT}"  > ~/.bashrc && \
    conda clean --all -y
ENV PATH /opt/conda/envs/${CONDA_ENVIRONMENT}/bin:$PATH

# Remove all sources
RUN rm -rf /src/*

# Copy all contents
WORKDIR /home
COPY . /home

EXPOSE 5003

CMD ["python", "app.py"]

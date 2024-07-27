# Dockerfile generated from its corresponding template and keys
# Base image for the container
FROM continuumio/miniconda3

WORKDIR /src

# Setup basic conda environment
ENV CONDA_ENVIRONMENT py_env
COPY environment.yml .

RUN apt update && apt-get install build-essential -y
RUN conda env create --file environment.yml && \
    echo "source activate ${CONDA_ENVIRONMENT}"  > ~/.bashrc && \
    conda clean --all -y
ENV PATH /opt/conda/envs/${CONDA_ENVIRONMENT}/bin:$PATH

# Remove all sources
RUN rm -rf /src/*

# Copy all contents
WORKDIR /home
COPY . /home

CMD [ "bash"]

###############################
FROM ubuntu:20.04

# Installazione strumenti base
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    default-jre \
    && rm -rf /var/lib/apt/lists/*

# Installazione di Biopython
RUN pip install biopython

# Creazione di una directory di lavoro
WORKDIR /workspace


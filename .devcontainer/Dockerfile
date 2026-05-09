FROM mcr.microsoft.com/devcontainers/base:ubuntu-24.04

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ansible \
        ansible-lint \
    && rm -rf /var/lib/apt/lists/*

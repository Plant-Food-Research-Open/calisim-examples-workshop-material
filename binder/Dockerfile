FROM ghcr.io/plant-food-research-open/calisim-examples-workshop:0.1.0

ARG NB_USER=jovyan

ARG NB_UID=1000

ENV USER ${NB_USER} 

ENV NB_UID ${NB_UID}

ENV HOME /home/${NB_USER}

ENV VIRTUAL_ENV=${HOME}/.venv \
    PATH="${HOME}/.venv/bin:$PATH"

RUN adduser --disabled-password \
    --gecos "Default user" \
    --uid ${NB_UID} \
    ${NB_USER} \
    && mv /workspace/{*,.*} ${HOME} 2>/dev/null \
    && chown -R ${NB_UID} ${HOME}

USER ${NB_USER}

WORKDIR ${HOME}
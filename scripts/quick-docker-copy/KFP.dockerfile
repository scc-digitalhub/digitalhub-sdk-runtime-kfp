ARG VERSION=
FROM ghcr.io/scc-digitalhub/digitalhub-sdk/wrapper-kfp:${VERSION}

ARG ROOT=/usr/local/lib/python3.9/site-packages

COPY ./digitalhub-sdk/digitalhub ${ROOT}/digitalhub
COPY ./digitalhub-sdk/runtimes/python/digitalhub_runtime_python ${ROOT}/digitalhub_runtime_python
COPY ./digitalhub-sdk/runtimes/container/digitalhub_runtime_container ${ROOT}/digitalhub_runtime_container
COPY ./digitalhub-sdk/runtimes/kfp/digitalhub_runtime_kfp ${ROOT}/digitalhub_runtime_kfp
COPY ./digitalhub-sdk/runtimes/dbt/digitalhub_runtime_dbt ${ROOT}/digitalhub_runtime_dbt
COPY ./digitalhub-sdk/runtimes/modelserve/digitalhub_runtime_modelserve ${ROOT}/digitalhub_runtime_modelserve
COPY ./digitalhub-sdk/wrapper/kfp/wrapper.py /app
COPY ./digitalhub-sdk/wrapper/kfp/step.py /app

USER root
RUN chown -R nonroot ${ROOT}/digitalhub*

USER 8877
FROM python:3.11.0-alpine3.15

# Make target platform available
ARG TARGETPLATFORM

# Build-time flags
ARG WITH_PLUGINS=true

# Copy files necessary installation
COPY requirements.txt requirements.txt
COPY requirements-plugins.txt requirements-plugins.txt

# Needed for native module builds
RUN apk add build-base git && \
    if [ "${TARGETPLATFORM}" = "linux/arm/v7" ]; then \
      apk add libxml2-dev libxslt-dev; \
    fi

# Perform mkdocs-material installation
RUN pip install --no-cache-dir -U pip
RUN pip install --no-cache-dir -r requirements.txt \
  && \
    if [ "${WITH_PLUGINS}" = "true" ]; then \
      pip install --no-cache-dir -r requirements-plugins.txt; \
    fi

# Set working directory
WORKDIR /docs

# Expose MkDocs development server port
EXPOSE 8000

# Start development server by default
ENTRYPOINT ["mkdocs"]
CMD ["serve", "--dev-addr=0.0.0.0:8000"]

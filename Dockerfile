# Usar una imagen base de Ubuntu
FROM deepset/haystack:cpu-v1.26.2

# The JSON schema is lazily generated at first usage, but we do it explicitly here for two reasons:
# - the schema will be already there when the container runs, saving the generation overhead when a container starts
# - derived images don't need to write the schema and can run with lower user privileges
RUN python3 -c "from haystack.utils.docker import cache_schema; cache_schema()"


# Haystack Preprocessor uses NLTK punkt model to divide text into a list of sentences.
# We cache these models for seamless user experience.
RUN python3 -c "from haystack.utils.docker import cache_nltk_model; cache_nltk_model()"

# Cache models
RUN python3 -c \
    "from haystack.utils.docker import cache_models; cache_models(['mrm8488/bert-base-spanish-wwm-cased-finetuned-spa-squad2-es'])"

# Set env vars for haystack api
ENV HAYSTACK_TELEMETRY_ENABLED=false

# Set the working directory
WORKDIR /app

FROM python:3.12-alpine

WORKDIR /app

COPY ./src/ /app/src/
COPY ./public/ /app/public/
COPY main.py pyproject.toml uv.lock /app/

# The installer requires curl (and certificates) to download the release archive
RUN apk add --no-cache curl ca-certificates

# Download the latest installer
ADD https://astral.sh/uv/install.sh /uv-installer.sh

# Run the installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Ensure the installed binary is on the `PATH`
ENV PATH="/root/.local/bin/:$PATH"

RUN uv sync

CMD ["uv", "run", "main.py"]
# CMD ["fastapi", "run", "app/main.py", "--port", "80"]
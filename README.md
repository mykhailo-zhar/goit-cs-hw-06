# Socket web app with MongoDB

A Python web application with no web framework. An HTTP server serves pages and static files. A UDP socket server receives form messages and stores them in MongoDB. The two servers run in separate processes, and in Docker they run in separate containers.

The app is meant to practice HTTP routing, socket I/O, Docker Compose, and writing MongoDB documents that match a real message record.

## How it works

```text
browser  --HTTP-->  http (main.py)  --UDP JSON-->  socket  --insert-->  MongoDB
```

1. The browser loads `/` or `/message`.
2. The form posts `username` and `message` to `POST /message`.
3. The HTTP server checks that both fields are present, then sends the payload as JSON over UDP.
4. The socket server inserts a document into the `messages` collection and reads it back after a short delay.

A successful post redirects to `/`. An empty username or message returns `public/error400.html` with status 400.

### HTTP routes

| Method | Path | Response |
| --- | --- | --- |
| GET | `/`, `/index` | `public/index.html` |
| GET | `/message` | `public/message.html` |
| GET | `/style.css`, `/logo.png` | static file from `public/` |
| GET | anything else | `public/error.html` (404) |
| POST | `/message` | redirect to `/`, or 400 if a field is empty |
| POST | anything else | `public/error.html` (404) |

### MongoDB document

Each stored message looks like this:

```json
{
  "date": "2026-09-25 12:00:00.123456",
  "username": "Krabat",
  "message": "Hello"
}
```

`date` is a UTC string in the form `%Y-%m-%d %H:%M:%S.%f`. MongoDB adds `_id`.

## Run with Docker Compose

From the repository root, after private variables are set (see below):

```bash
docker compose up --build
```

| Service | Published port | Role |
| --- | --- | --- |
| `http` | 3000 | HTTP server (`main.py`) |
| `socket` | 5000 | UDP socket server |
| `mongodb` | 27017 | MongoDB Atlas Local |

Open [http://127.0.0.1:3000](http://127.0.0.1:3000). Database files are stored in the named volume `data`, mounted at `/data` in the MongoDB container, so they survive container recreation.

## Environment variables

Public defaults live in [mise.toml](mise.toml) and apply when you run the app on the host with mise activated:

| Variable | Default | Meaning |
| --- | --- | --- |
| `HTTP_SERVER_HOST` | `127.0.0.1` | Address the HTTP server binds to. Compose leaves this unset, so the server listens on all interfaces inside the container. |
| `HTTP_SERVER_PORT` | `3000` | HTTP port |
| `SOCKET_MESSAGE_HOST` | `127.0.0.1` | UDP peer for the HTTP server, or bind address for the socket server |
| `SOCKET_MESSAGE_PORT` | `5000` | UDP port |

Compose sets these itself:

| Variable | Where | Meaning |
| --- | --- | --- |
| `SOCKET_MESSAGE_HOST` | `http` | `socket` (the Compose service name) |
| `SOCKET_MESSAGE_HOST` | `socket` | `0.0.0.0` |
| `CONTROL_SOCKET_SERVER` | `http` | On HTTP shutdown, send `END` so the socket server stops |
| `SOCKET_SERVER_DEPENDANT` | not set in Compose | When set, `main.py` starts the socket server in a child process. Compose starts that server as its own container instead. |
| `MONGODB_NOSERV` | `socket` | Use a direct `mongodb://` URI instead of `mongodb+srv://` |
| `MONGODB_HOST` | `socket` | `mongodb` |
| `MONGODB_PORT` | `socket` | `27017` |

### Private variables

Do not commit credentials. Put them in one of these files:

- **`mise.local.toml`** — mise loads this file automatically on top of `mise.toml`. With mise activated in your shell, the values are exported and Docker Compose can interpolate them. Do not commit this file.

  ```toml
  [env]
  MONGODB_USER = "app"
  MONGODB_PASSWORD = "change-me"
  ```

- **`.env`** — listed in `.gitignore`. Docker Compose reads it for `${MONGODB_USER}` and `${MONGODB_PASSWORD}` even when mise is not active.

  ```text
  MONGODB_USER=app
  MONGODB_PASSWORD=change-me
  ```

| Variable | Required for Compose | Meaning |
| --- | --- | --- |
| `MONGODB_USER` | yes | MongoDB user. Compose passes it to the database image and to the socket server. |
| `MONGODB_PASSWORD` | yes | MongoDB password |
| `MONGODB_HOST` | only outside Compose | Host for a direct or Atlas connection. Compose sets `mongodb`. |
| `MONGODB_APPNAME` | no | Optional Atlas application name, appended to the connection string |

Leave `MONGODB_NOSERV` unset to use a `mongodb+srv://` URI (Atlas). Set it, as Compose does, to connect to a single host with `MONGODB_PORT`.

## Local development

Tools:

- [mise](https://mise.jdx.dev/) for tool versions and environment variables
- [uv](https://docs.astral.sh/uv/) for dependencies and the virtual environment
- [pytest](https://pytest.org/) for tests
- [ruff](https://docs.astral.sh/ruff/) for linting
- [pre-commit](https://pre-commit.com/) for git hooks
- [Sphinx](https://www.sphinx-doc.org/) for API documentation

### Prerequisites

Install and activate [mise](https://mise.jdx.dev/getting-started.html) (for example `eval "$(mise activate bash)"` for Bash).

Python is pinned in [mise.toml](mise.toml) (default **3.12**, overridable with `PYTHON_VERSION`). The repo also has [.python-version](.python-version) for tooling that reads it.

### Quick start

1. Trust and install tools (from the repo root):

   ```bash
   mise trust
   mise install
   ```

   This installs Python, uv, and ruff. `python.uv_venv_auto` manages `.venv`.

2. Install dependencies from [pyproject.toml](pyproject.toml) and [uv.lock](uv.lock):

   ```bash
   uv sync
   ```

3. Install pre-commit hooks once per clone, after `uv sync`:

   ```bash
   mise run pre-commit-install
   ```

4. Add a dependency (updates `pyproject.toml` and `uv.lock`):

   ```bash
   uv add <package>
   ```

### Layout

- `src/` — application code. Sphinx autodoc is configured in [docs/source/conf.py](docs/source/conf.py).
- `public/` — HTML, CSS, and the logo.
- `tests/` — pytest tests.
- `docs/` — Sphinx documentation.
- `main.py` — HTTP entry point. Starts the socket server in another process when `SOCKET_SERVER_DEPENDANT` is set.
- [Dockerfile](Dockerfile) — image used by the `http` and `socket` services.
- [docker-compose.yml](docker-compose.yml) — HTTP server, socket server, and MongoDB.

### Common commands

| Goal | Command |
| --- | --- |
| Run tests | `mise run test` or `uv run pytest tests/` |
| Lint | `mise run lint` |
| Project / venv info | `mise run info` |
| Regenerate Sphinx API stubs | `mise run generate-docs` (`mise run gd`) |
| Build HTML docs | `mise run build-docs` (`mise run bd`) |
| Install pre-commit hooks | `mise run pre-commit-install` |

HTML output goes to `docs/build/` (open `docs/build/index.html` after a build).

After `sphinx-apidoc` adds `.rst` files under [docs/source](docs/source), include them in the `toctree` in [docs/source/index.rst](docs/source/index.rst) so they appear in the built site.

## License

See [LICENSE](LICENSE).

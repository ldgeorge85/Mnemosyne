# Test runner Dockerfile for backend integration tests
FROM python:3.11-slim

WORKDIR /app
COPY ./backend /app
COPY ./backend/requirements.txt /app/requirements.txt
COPY ./docker/wait-for-backend.py /wait-for-backend.py
RUN pip install --upgrade pip && pip install -r requirements.txt \
    && chmod +x /wait-for-backend.py

# pytest and httpx are already in requirements.txt

ENTRYPOINT ["/bin/sh", "-c", "/wait-for-backend.py && pytest --maxfail=3 --disable-warnings -v /app/tests/integration/"]

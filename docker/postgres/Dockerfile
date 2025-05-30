FROM pgvector/pgvector:pg15

# Copy initialization scripts
COPY init-pgvector.sql /docker-entrypoint-initdb.d/

# Expose PostgreSQL port
EXPOSE 5432

# Set default command
CMD ["postgres"]

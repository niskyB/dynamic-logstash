# Builder stage to generate Logstash config
FROM python:3.10-slim AS config_builder
WORKDIR /app
# Install psycopg2 module
RUN pip install psycopg2-binary python-dotenv

COPY generate_logstash_config.py .env /usr/share/logstash/

RUN python /usr/share/logstash/generate_logstash_config.py

# Final Logstash image
FROM docker.elastic.co/logstash/logstash:7.15.1

# Copy the generated Logstash configuration file from the builder stage
COPY --from=config_builder /app/logstash.conf /usr/share/logstash/pipeline/logstash.conf

# Add the PostgreSQL JDBC driver
ADD postgresql-42.7.1.jar /usr/share/logstash/logstash-core/lib/jars/

# Expose the Logstash port
EXPOSE 9600

CMD ["bin/logstash", "-f", "/usr/share/logstash/pipeline/logstash.conf"]

FROM docker.elastic.co/logstash/logstash:7.15.1

# Add the PostgreSQL JDBC driver
ADD postgresql-42.7.1.jar /usr/share/logstash/logstash-core/lib/jars/

# Add your Logstash configuration file
ADD logstash.conf /usr/share/logstash/pipeline/logstash.conf

CMD ["bin/logstash", "-f", "/usr/share/logstash/pipeline/logstash.conf"]
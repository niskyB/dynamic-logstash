# generate_logstash_config.py
import os

from dotenv import load_dotenv

import psycopg2


# Load environment variables from .env file

load_dotenv()


def get_tables_matching_pattern(host, user, password, database, pattern):

    # Connect to the database

    connection = psycopg2.connect(
        host=host, user=user, password=password, database=database, port=db_port
    )

    # Create a cursor object

    cursor = connection.cursor()

    # Execute SQL query to get tables matching the pattern

    query = "SELECT table_name FROM information_schema.tables WHERE table_name LIKE '{}'".format(
        pattern
    )

    cursor.execute(query)

    # Fetch all rows

    result = cursor.fetchall()

    # Extract table names from the result

    table_names = [row[0] for row in result]

    # Close the cursor and connection

    cursor.close()

    connection.close()

    return table_names


# Database connection parameters

host = os.getenv("DB_HOST")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
database = os.getenv("DB_DATABASE")
db_port = os.getenv("DB_PORT")
elastic_port = os.getenv("ELASTIC_PORT")

pattern = "App%"


# Get tables matching the pattern

table_names = get_tables_matching_pattern(host, user, password, database, pattern)


def generate_logstash_config(table_names):
    config = ""

    # Input section

    config += "input {\n"

    for table in table_names:

        config += f"  jdbc {{\n"

        config += f'    jdbc_driver_library => "/usr/share/logstash/logstash-core/lib/jars/postgresql-42.7.1.jar"\n'

        config += f'    jdbc_driver_class => "org.postgresql.Driver"\n'

        config += f'    jdbc_connection_string => "jdbc:postgresql://{host}:{db_port}/{database}"\n'

        config += f'    jdbc_user => "{user}"\n'

        config += f'    jdbc_password => "{password}"\n'

        config += f"    statement => 'SELECT * FROM \"{table}\"'\n"

        config += f'    tags => "{table}"\n'

        config += f"  }}\n"

    config += "}\n"

    # Output section

    config += "output {\n"

    for table in table_names:

        index_name = table.replace("App", "").lower()

        config += f'  if "{table}" in [tags] {{\n'

        config += f"    elasticsearch {{\n"

        config += f'      hosts => ["http://{host}:{elastic_port}"]\n'

        config += f'      index => "{index_name}"\n'

        config += f'      document_id => "%{{id}}"\n'

        config += f"    }}\n"

        config += f"  }}\n"

    config += "}\n"

    return config


# List of table names to be used in the Logstash configuration

# table_names = ["AppColors", "AppWards", "AppProvinceCities"]


# Generate Logstash configuration and print to stdout

logstash_config_content = generate_logstash_config(table_names)

with open("logstash.conf", "w") as logstash_config_file:
    logstash_config_file.write(logstash_config_content)

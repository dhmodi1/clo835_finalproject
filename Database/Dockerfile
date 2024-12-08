FROM mysql:8.0

# Set environment variables for MySQL root user and database
# These can be overridden at runtime using Docker environment variables.
ENV MYSQL_ROOT_PASSWORD=password
ENV MYSQL_DATABASE=employees

COPY ./mysql.sql /tmp

CMD [ "mysqld", "--init-file=/tmp/mysql.sql" ]


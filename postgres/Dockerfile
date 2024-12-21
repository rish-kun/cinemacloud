FROM postgres:16.4


# COPY ./postgresql.conf /var/lib/postgresql_conf/data/postgresql.conf
COPY .env.prod.db /var/lib/postgresql_conf/data/.env.prod.db
# RUN export $(cat /var/lib/postgresql_conf/data/.env.prod.db | xargs) && env
# CMD export $(xargs </var/lib/postgresql_conf/data/.env.prod.db)
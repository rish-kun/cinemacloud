FROM postgres:15

#Create non-root user
RUN adduser -D pguser && \
    mkdir -p /var/lib/postgresql/data && \
    chown -R pguser:pguser /var/lib/postgresql/data

# Copy custom postgres configuration
COPY --chown=pguser:pguser postgresql.conf /var/lib/postgresql/data/
COPY --chown=pguser:pguser pg_hba.conf /var/lib/postgresql/data/

# Security hardening
RUN chmod 600 /var/lib/postgresql/data/postgresql.conf && \
    chmod 600 /var/lib/postgresql/data/pg_hba.conf

USER pguser

COPY ./postgresql.conf /var/lib/postgresql/data/postgresql.conf
FROM openjdk:11-jre-slim

# Set environment variables
ENV FUSEKI_VERSION=4.10.0
ENV FUSEKI_HOME=/opt/fuseki
ENV FUSEKI_BASE=/fuseki-base
ENV JAVA_OPTIONS="-Xmx2g -Xms1g"

# Install wget and other utilities
RUN apt-get update && \
    apt-get install -y wget && \
    rm -rf /var/lib/apt/lists/*

# Download and install Fuseki
RUN mkdir -p ${FUSEKI_HOME} && \
    wget -O /tmp/fuseki.tar.gz "https://archive.apache.org/dist/jena/binaries/apache-jena-fuseki-${FUSEKI_VERSION}.tar.gz" && \
    tar -xzf /tmp/fuseki.tar.gz -C /tmp && \
    mv /tmp/apache-jena-fuseki-${FUSEKI_VERSION}/* ${FUSEKI_HOME}/ && \
    rm -rf /tmp/fuseki.tar.gz /tmp/apache-jena-fuseki-${FUSEKI_VERSION}

# Create fuseki base directory structure
RUN mkdir -p ${FUSEKI_BASE}/configuration && \
    mkdir -p ${FUSEKI_BASE}/databases && \
    mkdir -p ${FUSEKI_BASE}/logs && \
    mkdir -p ${FUSEKI_BASE}/system

# Create datasets directory for TDB2
RUN mkdir -p ${FUSEKI_BASE}/databases/tdb2-dataset

# Copy configuration files
COPY config/*.ttl ${FUSEKI_BASE}/configuration/

# Set working directory
WORKDIR ${FUSEKI_HOME}

# Expose port 3030
EXPOSE 3030

# Create startup script
RUN echo '#!/bin/bash\n\
# Start Fuseki server\n\
exec java ${JAVA_OPTIONS} -jar ${FUSEKI_HOME}/fuseki-server.jar \
--tdb2 \
--port=3030 \
--loc=${FUSEKI_BASE}/databases/tdb2-dataset/ \/ds' > /start-fuseki.sh && \
chmod +x /start-fuseki.sh

# Start Fuseki
CMD ["/start-fuseki.sh"]
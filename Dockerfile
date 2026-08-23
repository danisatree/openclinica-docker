# ============================================================
# OpenClinica Community Edition — Docker image
# Source tag: 3.17.2  (3.17.3 does not exist in the upstream
# repository; 3.17.2 is the nearest released tag on the 3.17.x
# line as of 2026-08-20)
# ============================================================

# ── Stage 1: build ──────────────────────────────────────────
FROM maven:3.8-openjdk-11 AS builder

WORKDIR /build

COPY fix_servlet.py /tmp/fix_servlet.py
COPY fix_jsp.py /tmp/fix_jsp.py
RUN apt-get update -qq && apt-get install -y --no-install-recommends git python3-minimal && \
    git clone --depth=1 --branch 3.17.2 \
        https://github.com/OpenClinica/OpenClinica.git . && \
    python3 /tmp/fix_servlet.py && \
    python3 /tmp/fix_jsp.py && \
    mvn clean package -DskipTests --no-transfer-progress \
        -DdbType=postgres \
        -DdbUser=clinica \
        -DdbPass=clinica \
        -Ddb=openclinica \
        -DdbPort=5432 \
        -DdbHost=oc-db \
        -DWEBAPP=OpenClinica \
        -DWEBAPP.lower=openclinica \
        "-Dcatalina.home=/usr/local/tomcat"

# ── Stage 2: runtime ────────────────────────────────────────
FROM tomcat:9-jre11

# Remove bundled default webapps (ROOT, examples, docs, …)
RUN rm -rf /usr/local/tomcat/webapps/*

# Main web application — pre-expand to patch ldap.host.
# The security config always tries the LDAP provider first. The default host
# (ldap://anaconda.isovera.local:389) is a .local mDNS name that hangs for
# ~8 seconds on every login before falling back to DB auth.  Pointing it at
# 127.0.0.1 makes the LDAP attempt fail instantly (connection refused).
COPY --from=builder \
    /build/web/target/OpenClinica-web-3.17.2.war \
    /usr/local/tomcat/webapps/OpenClinica.war
COPY fix_web.py /tmp/fix_web.py

RUN apt-get update -qq && \
    apt-get install -y --no-install-recommends unzip python3-minimal && \
    rm -rf /var/lib/apt/lists/* && \
    cd /usr/local/tomcat/webapps && \
    unzip -q OpenClinica.war -d OpenClinica && \
    rm OpenClinica.war && \
    sed -i 's|ldap\.host=ldap://.*|ldap.host=ldap://127.0.0.1:389|' \
        OpenClinica/WEB-INF/classes/datainfo.properties && \
    python3 /tmp/fix_web.py && \
    rm /tmp/fix_web.py

# Web-services endpoint — pre-expand so we can patch datainfo.properties.
# Root pom.xml has its <filters> block commented out, leaving ${log.dir} and
# similar tokens unresolved in the ws resource template, which causes a Logback
# circular-reference error at startup.  We inject a fully-resolved config file.
COPY --from=builder \
    /build/ws/target/OpenClinica-ws-3.17.2.war \
    /usr/local/tomcat/webapps/OpenClinica-ws.war

RUN cd /usr/local/tomcat/webapps && \
    unzip -q OpenClinica-ws.war -d OpenClinica-ws && \
    rm OpenClinica-ws.war && \
    PROPS=OpenClinica-ws/WEB-INF/classes/datainfo.properties && \
    sed -i \
        -e 's|\${filePath}|/usr/local/tomcat/openclinica.data/|g' \
        -e 's|\${userAccountNotification}|email|g' \
        -e 's|\${adminEmail}|admin@example.com|g' \
        -e 's|\${mailHost}|localhost|g' \
        -e 's|\${mailPort}|25|g' \
        -e 's|\${mailProtocol}|smtp|g' \
        -e 's|\${mailUsername}||g' \
        -e 's|\${mailPassword}||g' \
        -e 's|\${mailSmtpAuth}|false|g' \
        -e 's|\${mailSmtpStarttls\.enable}|false|g' \
        -e 's|\${mailSmtpsAuth}|false|g' \
        -e 's|\${mailSmtpsStarttls\.enable}|false|g' \
        -e 's|\${mailSmtpConnectionTimeout}|100|g' \
        -e 's|\${mailErrorMsg}|developers@openclinica.org|g' \
        -e 's|\${sysURL}|http://localhost:8080/OpenClinica/MainMenu|g' \
        -e 's|\${maxInactiveInterval}|3600|g' \
        -e 's|\${log\.dir}|/usr/local/tomcat/logs/openclinica-ws|g' \
        -e 's|\${logLocation}|local|g' \
        -e 's|\${logLevel}|info|g' \
        -e 's|\${syslog\.host}|localhost|g' \
        -e 's|\${syslog\.port}|514|g' \
        -e 's|\${org\.quartz\.jobStore\.misfireThreshold}|18000000|g' \
        -e 's|\${org\.quartz\.threadPool\.threadCount}|1|g' \
        -e 's|\${org\.quartz\.threadPool\.threadPriority}|5|g' \
        -e 's|\${ccts\.waitBeforeCommit}|6000|g' \
        -e 's|\${collectStats}|false|g' \
        -e 's|\${usage\.stats\.host}|usage.openclinica.com|g' \
        -e 's|\${usage\.stats\.port}|514|g' \
        -e 's|\${OpenClinica\.version}|3.17.2|g' \
        -e 's|\${designerURL}|https://designer13.openclinica.com/|g' \
        -e 's|\${version}|3.17.2|g' \
        "$PROPS"

# Pre-create the data directory referenced in datainfo.properties
RUN mkdir -p /usr/local/tomcat/openclinica.data

EXPOSE 8080
CMD ["catalina.sh", "run"]

FROM openjdk:16-jdk-alpine AS java-build-env
WORKDIR /app
COPY sdk-config.json .
COPY taxer-api.json .
COPY tools/swagger-codegen-cli-2.4.9.jar tools/
#-i http://host.docker.internal:7080/swagger.json
RUN java -jar tools/swagger-codegen-cli-2.4.9.jar generate \
	-i taxer-api.json \
	-c sdk-config.json \
	-l python \
	-o api-src


FROM python:3.9.0 as build-env

WORKDIR /app

RUN python3 -m pip install virtualenv
RUN virtualenv -p `which python3` venv

COPY . ./
COPY --from=java-build-env /app/api-src api-src/

RUN . venv/bin/activate && pip install --no-cache-dir . &&  pip install --no-cache-dir ./api-src &&\
  find /app/venv \( -type d -a -name test -o -name tests \) -o \( -type f -a -name '*.pyc' -o -name '*.pyo' \) -exec rm -rf '{}' \+

FROM python:3.9-alpine
LABEL Author="Max Sivkov"
LABEL E-mail="maxsivkov@gmail.com"
LABEL version="0.0.1"
STOPSIGNAL SIGINT

RUN apk update && \
    apk --no-cache --update add libstdc++ jq netcat-openbsd curl wget && \
    rm -rf /var/cache/apk/*


WORKDIR /app
COPY --from=build-env /app /app
RUN chmod a+x wait-for-http && chmod a+x entrypoint
ENV PATH="/app/venv/bin:/app:$PATH"

ENTRYPOINT ["python", "main.py"]
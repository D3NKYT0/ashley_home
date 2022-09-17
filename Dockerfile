FROM python:3.10.7

WORKDIR /ashley/

ENV JISHAKU_NO_UNDERSCORE=true

COPY ./requirements.txt /ashley/

RUN apt-get update; \
    apt-get upgrade -y; \
    pip install --upgrade pip; \
    apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false; \
    apt-get clean -y && rm -rf /var/lib/apt/lists/*;

RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT [ "python", "main.py" ] 

FROM ubuntu:18.04
WORKDIR /Bots/tonk
COPY requirements.txt .
RUN apt-get update && apt-get install -y python3 python3-dev python3-pip locales && locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8
RUN python3 -m pip install -U -r requirements.txt
COPY . .
CMD [ "python3", "tonk.py" ]
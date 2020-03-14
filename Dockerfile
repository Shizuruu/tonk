FROM ubuntu:latest
RUN echo Updating packages, installing python3.7 and pip
RUN apt-get update -y
RUN apt-get upgrade -y
RUN apt-get install -y python3-dev python3-pip
RUN python3 -m pip install --upgrade pip
RUN echo Copying the tonk directory into a service directory
COPY . /tonk
WORKDIR /tonk
RUN echo Installing Python packages listed in requirements.txt
RUN python3 -m pip install -r ./requirements.txt
RUN echo Starting python and the tonk service...
ENTRYPOINT ["python3"]
CMD ["tonk-dev.py"]

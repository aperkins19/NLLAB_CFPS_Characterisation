
# Dockerfile 04/2021
# Python environment for exporting data analysis for processing on remote systems. 

FROM ubuntu:20.04

# Updates ubuntu but with minimal dependences
RUN apt-get update && apt-get install --no-install-recommends --yes
# installs python
RUN apt-get install -y build-essential python3.6 python3-pip python3-dev
# disables pycaching
RUN export PYTHONDONTWRITEBYTECODE=1
# upgrades pip
RUN pip3 -q install pip --upgrade

RUN mkdir DataDashboard_app
WORKDIR /DataDashboard_app/
COPY . .
RUN pip3 install -r installation/requirements.txt

WORKDIR /DataDashboard_app/

EXPOSE 2051

HEALTHCHECK CMD curl --fail http://localhost:2051/_stcore/health

ENTRYPOINT ["streamlit", "run", "./webapp/Main.py", "--server.port=2051", "--server.address=0.0.0.0"]
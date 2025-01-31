# Python Based Docker
FROM python:3.10 as builder

# Installing Packages
RUN apt update && apt upgrade -y
RUN apt install git curl python3-pip ffmpeg -y

# Updating Pip Packages
RUN pip3 install -U pip

# Copying Requirements
COPY requirements.txt /requirements.txt

# Installing Requirements
RUN pip3 install -U -r /requirements.txt

FROM python:3.10-slim

COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
RUN mkdir /MissPerfectURL
WORKDIR /MissPerfectURL
COPY . /MissPerfectURL/
EXPOSE 8080
# Running MessageSearchBot
CMD ["python", "bot.py"]
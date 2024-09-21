FROM python:3.11-slim

LABEL name="MoodMate bot" \
      version="1.0" \
      maintainer="Mikhail Solovyanov <" \
      description="This is the Dockerfile for my mood tracker"

WORKDIR /

RUN apt-get update && apt-get install -y \
    build-essential \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/* &&\
    apt-get clean
# Copy the requirements.txt file to the container before copying the rest of the code
COPY requirements.txt /requirements.txt
COPY constraints.txt /constraints.txt

RUN pip3 install -r requirements.txt -c constraints.txt

COPY mood_mate_src /mood_mate_src

CMD ["python3", "-m", "mood_mate_src"]
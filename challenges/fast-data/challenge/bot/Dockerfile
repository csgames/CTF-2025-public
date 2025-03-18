FROM node:23-bookworm

RUN apt update
RUN DEBIAN_FRONTEND="noninteractive" apt install -y chromium

WORKDIR /app

# Setup
COPY package.json package-lock.json /app/
RUN npm install

COPY . /app

# Run
EXPOSE 1337

ENTRYPOINT ["node", "/app/index.js"]

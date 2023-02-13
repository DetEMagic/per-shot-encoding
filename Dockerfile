
FROM node:16-alpine as build-step
WORKDIR /app
COPY ./web-interface ./
RUN yarn install
RUN yarn build

FROM python:3.9
RUN useradd -r -u 666 videocore
WORKDIR /app
RUN mkdir ./web-interface
COPY --chown=666:666 --from=build-step /app/build ./web-interface/build

RUN ls
RUN mkdir ./backend
COPY --chown=666:666 ./backend ./backend
COPY --chown=666:666 ./config.yml ./config.yml
RUN pip install -r ./backend/requirements.txt
ENV FLASK_ENV production

EXPOSE 5000
WORKDIR /app/backend
CMD ["python", "server.py"]
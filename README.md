
# Krosus

Project in [Självständigt arbete i Informationsteknologi](https://www.uu.se/utbildning/utbildningar/selma/kursplan/?kKod=1DT350).

---

# Frontend

- Node
- NPM

Start by navigating to the `web-interface` folder.

In order to run the development version of the website, run:
```
npm start
```

Before static content can be served, the website must be "compiled". Do so by running:
```
npm run build
```

# Backend

- Requires
    - Python 3.7+ (along with pip)


## Processing video

The module for processing video is located in [backend/videolib/](./backend/videolib). The documentation for the module is in the file.

- Requires
    - FFmpeg (4.2.4+ should probably be fine), must be configured with `--enable-libvmaf` in order to run VMAF measurements.

 Note that most version of FFmpeg you download from package-managers and alike probably isn't configured with libvmaf. Double check this in the headers of your FFmpeg version and look for `--enable-libvmaf`.
 
To install ffmpeg on Ubuntu you can use the following command
```
sudo apt-get install ffmpeg
```

## Schedule API

The API for scheduling jobs is located in [backend/api/](./backend/api).

- Requires:
    - An available MySQL instance running on port 3306

If you do not have your own MySQL server, you can use the docker compose file located in `API/mysql-container`. With `docker-compose` installed, run the following in the container directory:
```
docker-compose up
```

In order for the API to know where the database to connect to is you must create a `config.yml` file that contains the following keys:
```yaml
db:
  host: db.com
  user: username
  password: password
  database: db

videolib:
  encoreUrl: https://videocore-encore.dev.aurora.svt.se
```

Make sure you have the static files for the website ready before starting the server. "Compile" the frontend by running the following command in `web-interface`:
```
npm run build
```

Before you can run the server, make sure you have installed all requirements listed in the `requirements.txt` file in `backend/`. You can do so by running the following command:
```
pip install -r backend/requirements.txt
```

Execute the following command to run the server:
```
python backend/server.py
```

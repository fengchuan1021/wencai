docker build . -t xtpythonimg --build-arg MODE=STAGE
docker ps | grep xtpython && docker stop xtpython
docker run -d --network myapp --ip 172.18.0.111 --rm -p8000:8000 -e MODE="STAGE" -e CMD="APP" --name xtpython xtpythonimg

docker ps | grep xtpythoncelery && docker stop xtpythoncelery
docker run -d --network myapp --rm  -e MODE="STAGE" -e CMD="CELERY" --name xtpythoncelery xtpythonimg

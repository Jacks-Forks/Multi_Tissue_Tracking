# Multi-Tissue-Tracking

[![Autos](https://img.shields.io/docker/cloud/automated/jackallope/tracking_docker?style=for-the-badge)](https://hub.docker.com/r/jackallope/tracking_docker) 
[![Build](https://img.shields.io/docker/cloud/build/jackallope/tracking_docker?style=for-the-badge)](https://hub.docker.com/r/jackallope/tracking_docker) 
[![Size](https://img.shields.io/docker/image-size/jackallope/tracking_docker?style=for-the-badge)](https://hub.docker.com/r/jackallope/tracking_docker)   

##### Update Image:
```
docker pull jackallope/tracking_docker:latest
```
##### Deployment on Cloud VM:
```
docker run --rm -d -p 8080:8080 -v ~/shared:/app/static/uploads jackallope/tracking_docker:latest
```
##### Webpage Access:
```
http://ip-of-machine:8080
```
###### Workflow:
![Diagram](https://jack.engineering/assets/flask_diagram.JPG)

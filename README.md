# site-scraper
A tool to automate some site watching tasks 


# HOW TO BUILD

docker build -t klimdos/scraper:0.0.1-alpha .


# HOW TO RUN

docker-compose up

<!-- docker network create selenium
docker run -d -p 4444:4444 --shm-size="2g" --net selenium --name worker  selenium/standalone-firefox:4.1.2-20220217
docker run -d -v /home/sasha/site-scraper/src/config.py:/app/config.py --restart unless-stopped --net selenium --name scraper scraper -->


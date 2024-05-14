Locally run:
docker run -it --rm -p 3000:3000 -v $PWD:/course -v "$PWD/pl_ag_jobs:/jobs" -e HOST_JOBS_DIR="$PWD/pl_ag_jobs" -v /var/run/docker.sock:/var/run/docker.sock --add-host=host.docker.internal:172.17.0.1 prairielearn/prairielearn:latest

https://stackoverflow.com/questions/72228079/docker-pull-from-local-repository-fails
docker run -d -p 5000:5000 --name registry registry:2
docker pull jryl/grader-snap
docker image tag jryl/grader-snap localhost:5000/snap-test-new
docker push localhost:5000/snap-test-new

docker build -t snap-test-new .

docker run -it --rm -p 3000:3000 -v %cd%:/course -v "%cd%/pl_ag_jobs:/jobs" -e HOST_JOBS_DIR="%cd%/pl_ag_jobs" -v /var/run/docker.sock:/var/run/docker.sock --add-host=host.docker.internal:172.17.0.1 prairielearn/prairielearn:latest
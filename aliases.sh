alias cshell="docker run -it -v $HOME/.aws:/root/.aws -v $(pwd):/app -w /app/scraper -e PYTHONPATH=/app/scraper/packages python:3.10-slim /bin/bash"

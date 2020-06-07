# [@scanmapchi](https://twitter.com/scanmapchi)

Twitter bot for https://scanmap.live/chi. Modified from https://twitter.com/scanmapny bot made by https://github.com/jdiedrick.

## Configuration

Create `config.py`:
`cp config.example.py config.py`

Then add your Twitter API credentials and update `LOG_URL` if needed.

## Usage
Running `main.py` will tweet the log entries that have been added since the timestamp in `./last_tweet`. If `./last_tweet` is not found, the script will just tweet the most recent entry.

### With docker

Build the image:
`docker build -t scanmapchi .`

Execute:
`docker run -v "$(pwd):/usr/src/app" scanmapchi`

### Without docker

Requires Python 3.6+

Install python modules:
`pip3 install -r requirements.txt`

Execute:
`python3 main.py`
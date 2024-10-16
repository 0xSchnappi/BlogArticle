import time

import redis
from flask import Flask
import redis.exceptions

app = Flask(__name__)
cache = redis.Redis(host="redis", port=6379)

def get_hit_count():
    retries = 5
    while True:
        try:
            return cache.incr('hits')
        except redis.exceptions.ConnectionError as exec:
            if retries == 0:
                raise exec
            retries -= 1
            time.sleep(0.5)
            
@app.route('/')
def hello():
    count = get_hit_count()
    return "Hello World! I have been seen {} times.\n".format(count)
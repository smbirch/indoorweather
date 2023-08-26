import gevent
from gevent import monkey
import schedule
import time

from prometheus_client import start_http_server

monkey.patch_all()

import outdoorweather
import sds011
import indoorweather


def get_all_stats():
    print("starting greenlets")
    greenlets = [
        gevent.spawn(sds011.get_indoor_stats),
        gevent.spawn(indoorweather.get_tempandhumidity),
        gevent.spawn(outdoorweather.get_current_weather),
        gevent.spawn(outdoorweather.get_current_aqi),
    ]
    gevent.joinall(greenlets)


def scheduler(interval):
    """runs schedule for functions

    Args:
        interval (int): time in seconds
    """
    while True:
        before = time.time()
        get_all_stats()
        print("\n***\n")
        duration = time.time() - before
        if duration < interval:
            time.sleep(interval - duration)
        else:
            print(
                "function duration exceeded %f interval (took %f)"
                % (interval, duration)
            )


def main():
    # start prometheus server
    start_http_server(9600)

    scheduler(180)


if __name__ == "__main__":
    main()

from gevent import monkey
monkey.patch_all()

import time
import sys

import outdoorweather
import sds011
import indoorweather

import gevent
from gevent import monkey

monkey.patch_all()


def get_all_stats():
    """Runs gevent greenlets and waits for completion"""
    print(time.strftime("%X %x %Z"))
    greenlets = [
        gevent.spawn(sds011.get_indoor_stats),
        gevent.spawn(indoorweather.get_tempandhumidity),
        gevent.spawn(outdoorweather.get_current_weather),
        gevent.spawn(outdoorweather.get_current_aqi),
    ]
    gevent.joinall(greenlets)


def scheduler(interval):
    """Runs schedule for functions

    Args:
        interval (int): Delay between polling sensors in seconds
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
    """Main"""
    scheduler(300)


if __name__ == "__main__":
    try:
        main()

    except KeyboardInterrupt:
        sys.exit()
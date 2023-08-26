import gevent
from gevent import monkey
import schedule
import time

monkey.patch_all()

import outdoorweather
import sds011
import indoorweather


def get_all_stats(greenlets):
    gevent.joinall(greenlets)
    print("\n***\n")


def main():
    # Create greenlets for each function call
    greenlets = [
        gevent.spawn(indoorweather.get_tempandhumidity),
        gevent.spawn(sds011.get_indoor_stats),
        gevent.spawn(outdoorweather.get_current_weather),
        gevent.spawn(outdoorweather.get_current_aqi),
    ]

    schedule.every(6).minutes.do(get_all_stats, greenlets)

    while True:
        schedule.run_pending()
        time.sleep(3)


if __name__ == "__main__":
    main()

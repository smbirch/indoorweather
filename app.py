import outdoorweather
import sds011
import indoorweather


if __name__ == "__main__":
    indoorweather.get_tempandhumidity()
    outdoorweather.get_current_weather()
    outdoorweather.get_current_aqi()
    sds011.get_indoor_stats()

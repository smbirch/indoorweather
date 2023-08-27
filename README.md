#### An Indoor Monitoring Solution

During the recent wildfires I discovered that my cat has asthma. 🥺

This project was created to monitor the temperature, humidity, and particulate density of the air in my home. 

### Tools and Technology
- Raspberry Pi 4B
- Python
- Open Weather API
- SDS011 Sensor
- DHT22 Sensor
- InfluxDB
- Grafana



### Do You want to Make One?
- Gather the materials above and install a fresh copy of [Debian](https://www.debian.org/download)/[Ubuntu](https://ubuntu.com/download/server)/[Raspbian](https://www.raspberrypi.com/software/) on the Pi. 
- Plug the sensors into your Pi. Your DHT22 requires a 5v pin, a neutral pin, and a data pin.
- Download this repo to your Pi. Also install pip3 and then use it to install pipenv.
- Install [InfluxDB](https://portal.influxdata.com/downloads/)
- Install [Grafana](https://grafana.com/)
- Create accounts and configure both services above
- Create an account with Open Weather API
	- Create an API key and stick it into a config.ini file:
		`[API] 
		`api_key = XXXXX`
- Run `pipenv install` in the directory you downloaded this repo to
- Run `pipenv shell` to enter the ENV shell
- Run `pipenv install`
- Run `python app.py`
- Come here and open issues if you encounter bugs 🙏


### Notes
The SDS011 sensor is ponderous, and not all of its *features* are outlined very well in the data sheet. By default the sensor will be set to active mode and will take readings once every couple of seconds until it loses power. However the diode inside only has an 8000 hour lifespan, or around 1 year. The easiest way to prolong this is to send a *sleep* signal to the sensor when not using it, then sending a *wake* signal when it is time to measure. In this code I have it set to grab metrics from each sensor and the Open Weather API every 5 minutes, and am putting the SDS011 sensor asleep in between. This has the dual purpose of not exceeding the daily 1000 API call limit set by Open Weather, as every reading makes two calls. 

The SDS011 also needs some time to clear out the sensor chamber before taking an accurate reading, and cannot make more than 1 reading every 3 seconds. If you experience a strange delay in the indoor AQI readings as compared to the other readings, this is why. Additionally, please note that this sensor is little endian, and prefers a 9600 baud.
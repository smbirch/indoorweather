#### An Indoor Monitoring Solution

During the recent wildfires I discovered that my cat has asthma. 🥺

This project was created to monitor the temperature, humidity, and particulate density of the air in my home.

### Tools and Technology
- Raspberry Pi
- Python
- Open Weather API
- SDS011 Sensor
- DHT22 Sensor
- Prometheus
- Grafana

I was unable to find a library which worked with the SDS011 sensor very well, and had to roll my own implementation. I am including the data sheet as a pdf in this repo in case anyone else has similar trouble finding it in the future. 
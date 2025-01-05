# PICO Agile Octopus Display
![e-ink device](images/case.jpg)

The display shows the Agile Octopus prices for the day. You can find a more detailed description of this project in [HackSpace Magazine Issue 72](https://hackspace.raspberrypi.com/issues/72)

# Getting Started
You will need a PICO-W device and a display. The code is written for the [Pimoroni e-ink](https://shop.pimoroni.com/products/pico-inky-pack) or [Pimoroni LCD](https://shop.pimoroni.com/products/pico-gfx-pack) devices. 
## Firmware Installation
Your PICO-W must be running the Pimoroni MicroPython image. You can find the version used for this project in the firmware project. Hold down the BOOTSEL button down on your PICO-W, plug it into your computer and then drag the image file onto the hard drive that appears.
## Sofware Installation
Once you have installed the firmware you can use the [Thonny program](https://thonny.org/)  to copy the **main.py** and **strptime.py** program files onto the display. Put them both in the root folder. 
## Software configuration

![configuration connect](/images/config1.png)
You will need to configure the display. You can use the online configuration tool to do this. Leave the PICO plugged into your computer and visit the page [https://pico-agile-octopus-display.github.io/config.github.io/](https://pico-agile-octopus-display.github.io/config.github.io/) 

Visit the web page, connect your display to a serial port and then click the "Display Plugged in" button.

![connect usb](/images/config2.png)

Select your device in the menu that appears and click "Connect". The web page will connect to the display and read the settings from it for you to edit.

![configure display](/images/config3.png)

When you've entered the setting values click "Submit" to send the values back into the display.

![configure complete](/images/config4.png)

When this page is displayed your device has been configured. It will reset but it might not connect correctly. Unplug it and plug it back in if you have this problem. 

If you select the wrong display type you might find that your display gets stuck. In that case plug the display into your computer and use Thonny to modify the settings.json file, or delete the file and you can then re-configure your device.

# Agile Tariffs

The Agile Octopus URL contains details of the energy product that you are using (AGILE-24-10-01 as of January 2025) and your tariff on that product (E-1R-AGILE-24-10-01-A for me in East Yorkshire). This gives me an Agile Octopus URL of:
```
https://api.octopus.energy/v1/products/AGILE-24-10-01/electricity-tariffs/E-1R-AGILE-24-10-01-A/standard-unit-rates/
```
You used to be able to get this from your account details, but this seems to be broken as of January 2025. There is a useful discussion of the issue on the Octopus Forum [here](https://forum.octopus.energy/t/agile-api-prices-very-late-today/11338/21). You may need to get a username and log in to view this. You can find out more about Agile Octopus pricing [here](https://octopus.energy/blog/agile-pricing-explained/#pricing).


| Letter Code | Region                             | DNO Company                                |
|-------------|------------------------------------|--------------------------------------------|
| A           | East England                      | UK Power Networks                          |
| B           | East Midlands                     | National Grid Electricity Distribution     |
| C           | London                            | UK Power Networks                          |
| D           | Merseyside, Cheshire, North Wales | SP Energy Networks                         |
| E           | West Midlands                     | National Grid Electricity Distribution     |
| F           | North East England                | Northern Powergrid                         |
| G           | North West England                | Electricity North West                     |
| P           | North Scotland                    | Scottish and Southern Electricity Networks |
| N           | South and Central Scotland        | SP Energy Networks                         |
| J           | South East England                | UK Power Networks                          |
| H           | Southern England                  | Scottish and Southern Electricity Networks |
| K           | South Wales                       | National Grid Electricity Distribution     |
| L           | South West England                | National Grid Electricity Distribution     |
| M           | Yorkshire                         | Northern Powergrid                         |

These are the letter codes that you add on the end of your tariff (in place of the A on the end of the code in the url above). My strong advice is to try different ones and compare them with the prices shown on your App or the web page. You can use the web config to change the URL.
# Display versions

![devices](/images/devices.jpg)

The software will work with these two displays.

# Case Design
You can find the designs for the case in the case folder on this site.

# Version 2.0
We are now on version two of the software. Changes:

* Updated the default settings for the latest tariff codes
* Added improved error handling and timeouts
* Screen now clears before a load so you can see when a box loses contact with the service

To get all the Version 2.0 goodness simply replace the main.py in your device with the latest one. 

Have fun!

Rob Miles

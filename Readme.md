# Wifi experiments under ESP32 SoCs

## Context

### M1 Internship at LS2N, Polytech Nantes, Summer 2021 - 

#### SmartComputerLab

[SmartComputerLab](http://www.smartcomputerlab.org/), conducted by [Przemyslaw BAKOWSKI](https://www.univ-nantes.fr/przemyslaw-bakowski), work around creating dev [IoT](https://en.wikipedia.org/wiki/Internet_of_things) kits using ARM or ESP32 [Architectures](https://en.wikipedia.org/wiki/Computer_architecture).

Currently, [Prof. BAKOWSKI](https://www.univ-nantes.fr/przemyslaw-bakowski) wants to experiment the capability to use a pretty new technology in ESP32 SoCs: [MicroPython](https://en.wikipedia.org/wiki/MicroPython).

#### Espressif

[Espressif](https://www.espressif.com/en) is the company working on the ESP32's [Architecture](https://en.wikipedia.org/wiki/Computer_architecture).

ESP32 is running on [FreeRTOS](https://en.wikipedia.org/wiki/FreeRTOS) and have specific functions developped as [ESP-IDF](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/), a framework made by [Espressif](https://www.espressif.com/en).

Some of these functions are really useful but not yes implemented under [MicroPython](https://en.wikipedia.org/wiki/MicroPython). Therefore, some people are already trying to implement specific [MicroPython](https://en.wikipedia.org/wiki/MicroPython) firmwares enabling these.

#### ESP-NOW

[ESP-NOW](https://www.espressif.com/en/products/software/esp-now/overview) is one of the [ESP-IDF](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/) functionalities we want to experiment, it is kind of a [Peer-to-Peer](https://en.wikipedia.org/wiki/Peer-to-peer) WiFi proprietary protocol whose aim is to have low energy comsuption.


Custom firmwares integrating [ESP-NOW](https://www.espressif.com/en/products/software/esp-now/overview) can be found here: https://github.com/glenn20/micropython-espnow-images

#### WiFi Sniffing

[ESP-IDF](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/) allow developpers to create easily a WiFi sniffer, their is currently no custom firmware allowing it in [MicroPython](https://en.wikipedia.org/wiki/MicroPython), therefore we are currently working on creating it.

## Installation

#### Python

```shell
# Debian-based
apt install python

# Arch-based
pacman -S python

# RedHat-based
dnf install python3
```

#### MicroPython

```shell
pip install esptool
```

#### Jupyter
You may use either JupyterLab or JupyterNotebook at your convenience

```shell
pip install jupyterlab
pip install notebook
```

Up to run MicroPython code under ESP32, a specific Jupyter Kernel is needed
pip install jupyter_micropython_kernel
python -m jupyter_micropython_kernel.install
Now run either JupyterLab or JupyterNotebook 

## Experiments

### ESP-NOW communication between two cards

The Master card will be connected to the Internet by WiFi and to the Slave by ESP-NOW, and has two roles :
- it will retrieve data from a server and send it to the Slave
- it will receive data from the Slave and send it to the server

The Slave card will be connected to the Master by ESP-NOW, and has two roles:
- it will receive data from the Master (and will process actions in real life)
- it will send data (from sensors in real life) to the Master


#### Install a Micropython firmware with ESP-NOW integration

You can find informations about this special firmware here :

https://micropython-glenn20.readthedocs.io/en/latest/library/espnow.html

Run this command in a MicroPython Notebook to write the firmware to the both serial ports :


```micropython
%esptool --port=1 esp32 esp-now.bin
%esptool --port=2 esp32 esp-now.bin
```


#### Connect to a serial port

Run this command in a MicroPython Notebook to connect to the choosed serial port :


```micropython
%serialconnect --port=1 --baud=115200
```

#### Enable a Wifi manager and Thingspeak communication on the Master device

The serial port connected need to be Master's.


```micropython
%serialconnect --port=1 --baud=115200

# The mpy-cross command is used to create byte code from a py file
%mpy-cross --set-exe ./mpy-cross

# WiFi Manager
%mpy-cross wifi_manager.py
# --binary is needed when sending a .mpy file
%sendtofile --binary --source ./wifi_manager.mpy /
%sendtofile --source ./boot_wifi_manager.py /boot.py

%mpy-cross --set-exe ./mpy-cross

# Thingspeak
%mpy-cross thingspeak.py
%sendtofile --binary --source ./thingspeak.mpy /

import machine
machine.reset()
```

The Wifi manager will create a Wifi Hotspot if it can't connect anywhere.

Then you need to connect a device to this Hotspot and access from a web browser to the address 192.168.4.1 and follow instructions.

#### Initialize ESP-NOW on both devices

Master


```micropython
%serialconnect --port=1 --baud=115200

import network
from esp import espnow
from thingspeak import post_thingspeak, get_thingspeak

wlan = network.WLAN(network.AP_IF)
wlan.active(True)
wlan.config(hidden=True)

# Prints Master's MAC
print(wlan.config('mac'))
```

Slave


```micropython
%serialconnect --port=2 --baud=115200

import network
from esp import espnow

wlan = network.WLAN(network.AP_IF)
wlan.config(hidden=True)
wlan.config(ps_mode=network.WIFI_PS_NONE)
wlan.active(True)

# Prints Slave's MAC
print(wlan.config('mac'))
```

#### Make Master and Slave peers

Master


```micropython
%serialconnect --port=1 --baud=115200

e = espnow.ESPNow()
e.init()

# Put here the Slave MAC printed
peer = b'L\x11\xae\x89\xbc\x95'

e.add_peer(peer, ifidx=network.AP_IF)
```

Slave



```micropython
%serialconnect --port=2 --baud=115200

e = espnow.ESPNow()
e.init()

# Put here the Master MAC printed
peer = b'L\x11\xae\x89\xbd\xd5'

e.add_peer(peer, ifidx=network.AP_IF)
```

#### Retrieve data from a server and send it to the Slave

[WARNING]: warning.png

![WARNING][WARNING] Don't run it here, only run it on master.ipynb and slave.ipynb to run both at the same moment ![WARNING][WARNING]


Master


```micropython
%serialconnect --port=1 --baud=115200

e.clear(True)
while True:
    if e.poll():
        last = None
        for host, msg in e:
            if msg and (str(msg, 'utf8') != last):
                last = str(msg, 'utf8')
                post_thingspeak("E13BHXREJ6K0V1DQ", [msg])
```

Slave


```micropython
%serialconnect --port=2 --baud=115200

import time

for i in range(5):
    print(i)
    ok = e.send(peer, str(i), True)
    while not ok:
        ok = e.send(peer, str(i), True)
    time.sleep(0.2)
```

#### Receive data from the Slave and send it to the server

[WARNING]: warning.png

![WARNING][WARNING] Don't run it here, only run it on master.ipynb and slave.ipynb to run both at the same moment ![WARNING][WARNING]

Master


```micropython
%serialconnect --port=2 --baud=115200

import time

last = ""
while True:
    data = get_thingspeak("179")
    print(data)
    if (data != last):
        last = data
        ok = e.send(peer, data, True)
        while not ok:
            ok = e.send(peer, data, True)
    time.sleep(1)
```

Slave


```micropython
%serialconnect --port=2 --baud=115200

e.clear(True)
while True:
    if e.poll():
        last = None
        for host, msg in e:
            if msg and (str(msg, 'utf8') != last):
                last = str(msg, 'utf8')
                print(msg)
```

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

[ESP-IDF](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/) allow developpers to create easily a WiFi sniffer, while it is not currently added in [MicroPython](https://en.wikipedia.org/wiki/MicroPython), we forked [MicroPython](https://en.wikipedia.org/wiki/MicroPython) to https://github.com/Albaobab/micropython with this functionality.

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

```shell
pip install jupyter_micropython_kernel
python -m jupyter_micropython_kernel.install
```

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


```python
%esptool --port=1 esp32 bin/esp-now.bin
%esptool --port=2 esp32 bin/esp-now.bin
%esptool --port=3 esp32 bin/esp-now.bin
```


#### Connect to a serial port

Run this command in a MicroPython Notebook to connect to the choosed serial port :


```python
%serialconnect --port=1 --baud=115200
```

#### Enable a Wifi manager and Thingspeak communication on the Master device

The serial port connected need to be Master's.


```python
%serialconnect --port=1 --baud=115200

# The mpy-cross command is used to create byte code from a py file
%mpy-cross --set-exe ./mpy-cross

# WiFi Manager
%mpy-cross lib/wifi_manager.py
# --binary is needed when sending a .mpy file
%sendtofile --binary --source lib/wifi_manager.mpy /
%sendtofile --source lib/boot_wifi_manager.py /boot.py

%mpy-cross --set-exe ./mpy-cross

# Thingspeak
%mpy-cross lib/thingspeak.py
%sendtofile --binary --source lib/thingspeak.mpy /

import machine
machine.reset()
```

The Wifi manager will create a Wifi Hotspot if it can't connect anywhere.

Then you need to connect a device to this Hotspot and access from a web browser to the address 192.168.4.1 and follow instructions.

#### Initialize ESP-NOW on both devices

Master


```python
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


```python
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


```python
%serialconnect --port=3 --baud=115200

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


```python
%serialconnect --port=1 --baud=115200

e = espnow.ESPNow()
e.init()

# Put here the Slaves MACs printed
e.add_peer(b'$o(\xc8\x01%', ifidx=network.AP_IF)
e.add_peer(b"\xfc\xf5\xc4'\xcc1", ifidx=network.AP_IF)
```

Slave



```python
%serialconnect --port=2 --baud=115200

e = espnow.ESPNow()
e.init()

# Put here the Master MAC printed
peer = b'L\x11\xae\x89\xbd\xd5'

e.add_peer(peer, ifidx=network.AP_IF)
```


```python
%serialconnect --port=3 --baud=115200

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


```python
%serialconnect --port=1 --baud=115200
def prettify(byte_array):
    return ':'.join('%02x' % int(b) for b in byte_array)

e.clear(True)
while True:
    if e.poll():
        last = None
        for host, msg in e:
            if msg and (str(msg, 'utf8') != last):
                last = str(msg, 'utf8')
                post_thingspeak("E13BHXREJ6K0V1DQ", [msg, prettify(host)], proxy="193.52.104.20", proxy_port=3128)
```

Slave


```python
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


```python
%serialconnect --port=1 --baud=115200

import time

# Broadcast address to send to every Slaves
peer = b'\xff\xff\xff\xff\xff\xff'
e.add_peer(peer)

last = ""
while True:
    data = get_thingspeak("179", "193.52.104.20", 3128)
    print(data)
    if (data != last):
        last = data
        ok = e.send(peer, data, True)
        while not ok:
            ok = e.send(peer, data, True)
    time.sleep(1)
```

Slave


```python
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

### Wifi Sniffing

#### Modifying [MicroPython](https://en.wikipedia.org/wiki/MicroPython)'s code base

Up to use C libraries inside [MicroPython](https://en.wikipedia.org/wiki/MicroPython), we need to understand how Python objects are transformed to C types and inversely.

Complete files shown below can be found in the [Github repository of Micropython](https://github.com/micropython/micropython).

Every single type is a simple pointer interpreted as whatever we want.

##### `py/obj.h`
```c
...
typedef void *mp_obj_t;
typedef const void *mp_const_obj_t;
...
```

For example, if we want to transform an integer given by a C library to a MicroPython integer object, we can use `mp_obj_new_int`.

##### `py/obj.h`
```c
...
#define MP_OBJ_NEW_SMALL_INT(small_int) ((mp_obj_t)((((mp_uint_t)(small_int)) << 2) | 1))
...
mp_obj_t mp_obj_new_int(mp_int_t value);
...
```
##### `py/objint.c`
```c
mp_obj_t mp_obj_new_int(mp_int_t value) {
    if (MP_SMALL_INT_FITS(value)) {
        return MP_OBJ_NEW_SMALL_INT(value);
    }
    mp_raise_msg(&mp_type_OverflowError, MP_ERROR_TEXT("small int overflow"));
    return mp_const_none;
}
...
```

In the other side, calling `mp_obj_get_int` will able to get an integer from a MicroPython object and to return it to the user.

##### `ports/esp32/mpconfigport.h`
```c
...
typedef int32_t mp_int_t;
...
```
##### `py/obj.h`
```c
...
#define MP_OBJ_SMALL_INT_VALUE(o) (((mp_int_t)(o)) >> 1)
...
mp_int_t mp_obj_get_int(mp_const_obj_t arg);
...
```
##### `py/objint.c`
```c
...
mp_int_t mp_obj_get_int(mp_const_obj_t arg) {
    if (arg == mp_const_false) {
        return 0;
    } else if (arg == mp_const_true) {
        return 1;
    } else if (mp_obj_is_small_int(arg)) {
        return MP_OBJ_SMALL_INT_VALUE(arg);
    } else if (mp_obj_is_type(arg, &mp_type_int)) {
        return mp_obj_int_get_checked(arg);
    } else {
        mp_obj_t res = mp_unary_op(MP_UNARY_OP_INT, (mp_obj_t)arg);
        return mp_obj_int_get_checked(res);
    }
}
...
```

The easiest and most light weight way to create an object-like return value is using MicroPython tuples this way :

```c
mp_obj_t raw_tuple[] = {
    mp_obj_new_tuple(number_of_objects_in_another_raw_tuple, another_raw_tuple),
    mp_obj_new_bytes(byte_array, length_of_byte_array),
    mp_obj_new_int(10),
};

mp_obj_t tuple = mp_obj_new_tuple(3, raw_tuple);
```

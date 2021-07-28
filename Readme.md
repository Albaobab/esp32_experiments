# Wifi experiments under ESP32 SoCs

## Context

### M1 Internship at LS2N, Polytech Nantes, Summer 2021

#### SmartComputerLab

[SmartComputerLab](http://www.smartcomputerlab.org/), conducted by [Przemyslaw BAKOWSKI](https://www.univ-nantes.fr/przemyslaw-bakowski), works around creating dev [IoT](https://en.wikipedia.org/wiki/Internet_of_things) kits using ARM or ESP32 [Architectures](https://en.wikipedia.org/wiki/Computer_architecture).

Currently, [Prof. BAKOWSKI](https://www.univ-nantes.fr/przemyslaw-bakowski) wants to experiment the capability to use a quite new technology in ESP32 SoCs: [MicroPython](https://en.wikipedia.org/wiki/MicroPython).

#### Espressif

[Espressif](https://www.espressif.com/en) is the company working on the ESP32's [Architecture](https://en.wikipedia.org/wiki/Computer_architecture).

ESP32 is running on [FreeRTOS](https://en.wikipedia.org/wiki/FreeRTOS) and has specific functions defined in [ESP-IDF](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/), a framework made by [Espressif](https://www.espressif.com/en).

Some of these functions are really useful but not yet implemented under [MicroPython](https://en.wikipedia.org/wiki/MicroPython). Therefore, some people are already trying to implement specific [MicroPython](https://en.wikipedia.org/wiki/MicroPython) firmwares enabling them.

#### ESP-NOW

[ESP-NOW](https://www.espressif.com/en/products/software/esp-now/overview) is one of the [ESP-IDF](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/) functionalities we want to experiment, is a WiFi proprietary protocol whose aim is to have low energy consumption.


Custom firmwares integrating [ESP-NOW](https://www.espressif.com/en/products/software/esp-now/overview) can be found here: https://github.com/glenn20/micropython-espnow-images

#### WiFi Sniffing

[ESP-IDF](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/) allows developpers to easily create a WiFi sniffer. While it is not currently added in [MicroPython](https://en.wikipedia.org/wiki/MicroPython), we forked [MicroPython](https://en.wikipedia.org/wiki/MicroPython) to https://github.com/Albaobab/micropython with this functionality.

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

The Master card will be connected to the Internet by WiFi and to the Slaves by ESP-NOW, and has two roles :
- it will retrieve data from a server and send it to the Slaves
- it will receive data from the Slaves and send it to the server

The Slaves cards will be connected to the Master by ESP-NOW, and has two roles:
- it will receive data from the Master (and will process actions in practical cases)
- it will send data (from sensors in practical cases) to the Master


#### Install a Micropython firmware with ESP-NOW integration

You can find informations about this specific firmware here :

https://micropython-glenn20.readthedocs.io/en/latest/library/espnow.html

Run this command in a MicroPython Notebook to write the firmware to both serial ports :


```python
%esptool --port=1 esp32 bin/esp-now.bin
%esptool --port=2 esp32 bin/esp-now.bin
%esptool --port=3 esp32 bin/esp-now.bin
```


#### Connect to a serial port

Run this command in a MicroPython Notebook to connect to the choosen serial port :


```python
%serialconnect --port=1 --baud=115200
```

#### Enable a Wifi manager and Thingspeak communication on the Master device

The serial port connected needs to be Master's.


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

The Wifi manager will create a Wifi Hotspot if it cannot connect anywhere.

Then you need to connect a device to this Hotspot and access the address `192.168.4.1` from a web browser and follow the instructions.

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

![WARNING][WARNING] Don't run it here, only run it on master.ipynb and slave.ipynb to run both at the same time ![WARNING][WARNING]


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

![WARNING][WARNING] Don't run it here, only run it on master.ipynb and slave.ipynb to run both at the same time ![WARNING][WARNING]

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

### Modifying [MicroPython](https://en.wikipedia.org/wiki/MicroPython)'s code base

Up to use C libraries inside [MicroPython](https://en.wikipedia.org/wiki/MicroPython), we need to understand how Python objects are transformed into C types and vice versa.

Complete files shown below can be found in the [Github repository of Micropython](https://github.com/micropython/micropython).

Every [MicroPython](https://en.wikipedia.org/wiki/MicroPython) object is a `mp_obj_t`.

##### `py/obj.h`
```c
...
typedef void *mp_obj_t;
typedef const void *mp_const_obj_t;
...
```

For example, if we want to transform an integer given by a C library into a MicroPython integer object, we can use `mp_obj_new_int`.

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
...
mp_obj_t mp_obj_new_int(mp_int_t value) {
    if (MP_SMALL_INT_FITS(value)) {
        return MP_OBJ_NEW_SMALL_INT(value);
    }
    mp_raise_msg(&mp_type_OverflowError, MP_ERROR_TEXT("small int overflow"));
    return mp_const_none;
}
...
```

On the other side, calling `mp_obj_get_int` will allow you to get an integer from a MicroPython object and to return it to the user.

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

The easiest and most light weight way to create an object-like return value is using MicroPython tuples like this :

```c
mp_obj_t raw_tuple[] = {
    mp_obj_new_tuple(number_of_objects_in_another_raw_tuple, another_raw_tuple),
    mp_obj_new_bytes(byte_array, length_of_byte_array),
    mp_obj_new_int(10),
};

mp_obj_t tuple = mp_obj_new_tuple(3, raw_tuple);
```

Thanks to the these [MicroPython](https://en.wikipedia.org/wiki/MicroPython) functions and [ESP-IDF promiscuous functions](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/network/esp_wifi.html?highlight=promiscuous#_CPPv430esp_wifi_set_promiscuous_rx_cb21wifi_promiscuous_cb_t), we have implemented a WiFi Sniffer used next.

### WiFi Sniffing

Install the firmware with the WiFi sniffer firmware.



```python
%esptool --port=0 esp32 bin/promiscuous.bin
```

Then, we need to activate the promiscuous mode of the WiFi interface.


```python
%serialconnect --port=0 --baud=115200

import network
import time
wlan = network.WLAN()
wlan.active(True)
# Activates the promiscuous mode
wlan.config(promiscuous=True)
```

#### Type Filters

`FILTER_MASK_MGMT`

    filter the packets with type of WIFI_PKT_MGMT

`FILTER_MASK_CTRL`

    filter the packets with type of WIFI_PKT_CTRL

`FILTER_MASK_DATA`

    filter the packets with type of WIFI_PKT_DATA

`FILTER_MASK_MISC`

    filter the packets with type of WIFI_PKT_MISC

`FILTER_MASK_DATA_MPDU`

    filter the MPDU which is a kind of WIFI_PKT_DATA

`FILTER_MASK_DATA_AMPDU`

    filter the AMPDU which is a kind of WIFI_PKT_DATA

`FILTER_MASK_FCSFAIL`

    filter the FCS failed packets, do not open it in general

#### Subtypes Filters

`CTRL_FILTER_MASK_ALL`

    filter all control packets

`CTRL_FILTER_MASK_WRAPPER`

    filter the control packets with subtype of Control Wrapper

`CTRL_FILTER_MASK_BAR`

    filter the control packets with subtype of Block Ack Request

`CTRL_FILTER_MASK_BA`

    filter the control packets with subtype of Block Ack

`CTRL_FILTER_MASK_PSPOLL`

    filter the control packets with subtype of PS-Poll

`CTRL_FILTER_MASK_RTS`

    filter the control packets with subtype of RTS

`CTRL_FILTER_MASK_CTS`

    filter the control packets with subtype of CTS

`CTRL_FILTER_MASK_ACK`

    filter the control packets with subtype of ACK

`CTRL_FILTER_MASK_CFEND`

    filter the control packets with subtype of CF-END

`CTRL_FILTER_MASK_CFENDACK`

    filter the control packets with subtype of CF-END+CF-ACK

##### `example:`


```python
wlan.config(type_filter=network.FILTER_MASK_MGMT, subtype_filter=network.CTRL_FILTER_MASK_ALL)
```

#### Reading returned values

`find_packet` function take the WiFi channel wanted as parameter.

It returns a tuple object defined this way:

`[0]` - It is equals to `network.NEW_PACKET` if the packet data is different than the last found or `network.SAME_PACKET` if it is the same one. 

Other values are only send if this one `[0]` is equals to `network.NEW_PACKET`.

`[1]` - It contains a tuple object containing metadata defined this way:

* `[0]` Received Signal Strength Indicator(RSSI) of packet. unit: dBm
* `[1]` PHY rate encoding of the packet. Only valid for non HT(11bg) packet 
* `[2]` 0: non HT(11bg) packet; 1: HT(11n) packet; 3: VHT(11ac) packet
* `[3]` Modulation Coding Scheme. If is HT(11n) packet, shows the modulation, range from 0 to 76(MSC0 ~ MCS76)
* `[4]` Channel Bandwidth of the packet. 0: 20MHz; 1: 40MHz
* `[5]` Aggregation. 0: MPDU packet; 1: AMPDU packet
* `[6]` Space Time Block Code(STBC). 0: non STBC packet; 1: STBC packet
* `[7]` Flag is set for 11n packets which are LDPC
* `[8]` Short Guide Interval(SGI). 0: Long GI; 1: Short GI
* `[9]` Noise floor of Radio Frequency Module(RF). unit: 0.25dBm
* `[10]` Primary channel on which this packet is received
* `[11]` Secondary channel on which this packet is received. 0: none; 1: above; 2: below
* `[12]` Timestamp. The local time when this packet is received. It is precise only if modem sleep or light sleep is not enabled. unit: microsecond
* `[13]` Antenna number from which this packet is received. 0: WiFi antenna 0; 1: WiFi antenna 1
* `[14]` Length of packet including Frame Check Sequence(FCS)
* `[15]` State of the packet. 0: no error; others: error numbers which are not public

`[2]` - It contains the raw WiFi packet found.

`[3]` - It contains the WiFi packet type found.

#### Using the new `find_packet` function

Here is a sample trying to find MAC addresses of devices communicating by WiFi over three different WiFi channels


```python
%serialconnect --port=0 --baud=115200
import utime

wlan.config(type_filter=network.FILTER_MASK_ALL)

found = set()

def find_users(chan):
    print("Start finding MAC on the channel " + chan)
    t = utime.time()
    p = wlan.find_packet(chan)

    while p != None and p[0] == network.NEW_PACKET and (utime.time() + 30 > t):
        found.add(p[2][10:16])

        p = wlan.find_packet(chan)
    print("Stop finding MAC on the channel " + chan)

find_users(1)
find_users(6)
find_users(11)

print("MAC addresses found: " + found)
```

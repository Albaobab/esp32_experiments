# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()

import wifi_manager

wifi_manager.write_profiles({'Turtlebot': 'Turtlebot'})
STA_WLAN = wifi_manager.get_connection()
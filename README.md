Driver for ST7735 display using WiPy 2.0
------------------------------------------------
This library allows to connect a ST7735 Display to a WiPy 2.0 and includes some drawing tools (line, circle, rectangle).

Wiring
-----------------------

|		|		|		|
|:-----:|:-----:|:-----:|
|**Wipy 2.0**|	|**ST7735**|
| `3.3v`| 	 | `VCC`|
| `GND` | 	 | `GND`|
| `P6`(`G13`) |   |	 `RES`  |
| `P7`(`G14`) |   |	 `RS/DC`  |
| `P8`(`G15`) |   |	 `CS`  |
| `P10`(`G17`) |   |	 `SCL`  |
| `P11`(`G22`) |   |	 `SDA`  |

These are the default connection setting, you can change them using the constructor of the `Display` class as
```
my_display = Display(self, uSPI=0, pinDC='P7', pinCS='P8', pinRST='P6')   
```

Use:
----------
```
from graphics import Display
from fonts import font_6x8	# only needed for drawString or drawChar methods

my_display = Display()
my_display.clearScreen() # ClearScreen
my_display.drawString(10,10,'LeMaRiva', font_6x8, my_display.COLOR_RED, 2)    
```

More Info:
-----------
* Blog article: http://lemariva.com/blog/2017/01/wipy-2-0-weather-report-box

Credits:
---------------
* Rewriten from: http://forum.43oh.com/topic/4352-universal-color-lcd-graphics-library-2/

License:
---------------
* Apache 2.0 (check files)

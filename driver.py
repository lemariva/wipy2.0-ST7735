#Copyright [2017] [Mauro Riva <lemariva@mail.com> <lemariva.com>]

#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at

#http://www.apache.org/licenses/LICENSE-2.0

#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.

#The above copyright notice and this permission notice shall be
#included in all copies or substantial portions of the Software.  

from machine import Pin, SPI
import time

class driver:
    """           
    Command definitions
    """
    CMD_NOP     = const(0x00) # No Operation
    CMD_SWRESET = const(0x01) # Software reset
    CMD_RDDID   = const(0x04) # Read Display ID
    CMD_RDDST   = const(0x09) # Read Display Status
    
    CMD_SLPIN   = const(0x10) # Sleep in & booster off
    CMD_SLPOUT  = const(0x11) # Sleep out & booster on
    CMD_PTLON   = const(0x12) # Partial mode on
    CMD_NORON   = const(0x13) # Partial off (Normal)
    
    CMD_INVOFF  = const(0x20) # Display inversion off
    CMD_INVON   = const(0x21) # Display inversion on
    CMD_DISPOFF = const(0x28) # Display off
    CMD_DISPON  = const(0x29) # Display on
    CMD_CASET   = const(0x2A) # Column address set
    CMD_RASET   = const(0x2B) # Row address set
    CMD_RAMWR   = const(0x2C) # Memory write
    CMD_RAMRD   = const(0x2E) # Memory read
    
    CMD_PTLAR   = const(0x30) # Partial start/end address set
    CMD_COLMOD  = const(0x3A) # Interface pixel format
    CMD_MADCTL  = const(0x36) # Memory data access control
    
    CMD_RDID1   = const(0xDA) # Read ID1
    CMD_RDID2   = const(0xDB) # Read ID2
    CMD_RDID3   = const(0xDC) # Read ID3
    CMD_RDID4   = const(0xDD) # Read ID4
    
    """
    Panel function commands    
    """
    
    CMD_FRMCTR1 = const(0xB1) # In normal mode (Full colors)
    CMD_FRMCTR2 = const(0xB2) # In Idle mode (8-colors)
    CMD_FRMCTR3 = const(0xB3) # In partial mode + Full colors
    CMD_INVCTR  = const(0xB4) # Display inversion control
    
    CMD_PWCTR1  = const(0xC0) # Power control settings
    CMD_PWCTR2  = const(0xC1) # Power control settings
    CMD_PWCTR3  = const(0xC2) # In normal mode (Full colors)
    CMD_PWCTR4  = const(0xC3) # In Idle mode (8-colors)
    CMD_PWCTR5  = const(0xC4) # In partial mode + Full colors
    CMD_VMCTR1  = const(0xC5) # VCOM control
    
    CMD_GMCTRP1 = const(0xE0)
    CMD_GMCTRN1 = const(0xE1)
            

    def __init__(self, uSPI=0, pinDC='P7', pinCS='P8', pinRST='P6', bl=None):        
        """
        SPI      - SPI Bus (CLK/MOSI/MISO)
        DC       - RS/DC data/command flag
        CS       - Chip Select, enable communication
        RST/RES  - Reset
        BL/Lite  - Backlight control
        """        
        self.spi = self.spi = SPI(uSPI, SPI.MASTER, baudrate=8000000, polarity=0, phase=0, firstbit=SPI.MSB)   
        self.dc  = Pin(pinDC, Pin.OUT, Pin.PULL_DOWN)
        self.cs  = Pin(pinCS, Pin.OUT, Pin.PULL_DOWN)
        self.rst = Pin(pinRST, Pin.OUT, Pin.PULL_DOWN)            
        self.bl  = bl        

    def write_cmd(self, cmd):
        """
        Display command write implementation using SPI.
        """        
        self.dc.value(0)        #LCD_DC_LOW;
        self.cs.value(0)        #LCD_SELECT;        
        self.spi.write(cmd)
        self.cs.value(1)        #LCD_DESELECT;

    def write_data(self, data):
        """
        Display data write implementation using SPI.
        """        
        self.dc.value(1)        #LCD_DC_HI;
        self.cs.value(0)        #LCD_SELECT;        
        self.spi.write(data)
        self.cs.value(1)        #LCD_DESELECT;
        
    def write_pixels(self, count, color):
        """
        Write pixels to the display.
        count - total number of pixels
        color - 16-bit RGB value
        """
        self.dc.value(1)
        self.cs.value(0)
        for _ in range(count):
            self.spi.write(color)
        self.cs.value(1)
        
    def backlight(self, state=None):
        """
        Get or set the backlight status if the pin is available.
        """
        if self.bl is None:
            return None
        else:
            if state is None:
                return self.backlight_on
            self.bl.value(1 if state else 0)
            self.backlight_on = stat        
            
    def reset(self):
        """
        Hard reset the display.
        """
        self.dc.value(0)
        self.rst.value(1)
        time.sleep_ms(500)
        self.rst.value(0)
        time.sleep_ms(500)
        self.rst.value(1)
        time.sleep_ms(500)            
            
class ST7735(driver):
        
    margin_row = 0      # set column and row margins
    margin_col = 0    
        
    _orientation = 0    # actual orientation
    
    def __init__(self, uSPI=0, pinDC='P7', pinCS='P8', pinRST='P6', bl=None):
        super().__init__(uSPI, pinDC, pinCS, pinRST, bl)

    def init(self):

        self.reset()    # Hardware reset    

        self.write_cmd(driver.CMD_SWRESET)
        time.sleep_ms(20)
        self.write_cmd(driver.CMD_SLPOUT)
        time.sleep_ms(255)      # driver is doing self check, but seems to be working fine without the delay

        self.write_cmd(driver.CMD_COLMOD)
        self.write_data(0x05)   # 16-bit mode

        self.setOrientation()

        self.gammaAdjustmentST7735()
        
        self.write_cmd(driver.CMD_DISPON)   # CMD_DISPON should be set on power up, sleep out should be enough

        
    def setOrientation(self, orientation=3):        
        """
        Set the display orientation 
        """               
        self.write_cmd(driver.CMD_MADCTL)
        
        if(orientation == 1):
            self.write_data(0x68)
            self._orientation = 1       
        elif(orientation == 2):
            self.write_data(0x08)
            self._orientation = 2          
        elif(orientation == 3):
            self.write_data(0xA8)
            self._orientation = 3           
        else:
            self.write_data(0xC8)
            self._orientation = 0
        
        
    def gammaAdjustmentST7735(self):
        """
        Gamma correction is needed for accurate color but is not necessary.
        """        
        self.write_cmd(driver.CMD_GMCTRP1)
        self.write_data(bytearray([0x02, 0x1c, 0x07, 0x12, 0x37, 0x32,
                                   0x29, 0x2d, 0x29, 0x25, 0x2b, 0x39, 0x00, 0x01, 0x03, 0x10]))
        
        self.write_cmd(driver.CMD_GMCTRN1)        
        self.write_data(bytearray([0x03, 0x1d, 0x07, 0x06, 0x2e, 0x2c,
                                   0x29, 0x2d, 0x2e, 0x2e, 0x37, 0x3f, 0x00, 0x00, 0x02, 0x10]))        
        
    
    def setArea(self, xStart, yStart, xEnd, yEnd):
        """
        Set window frame boundaries.
        Any pixels written to the display will start from this area.
        """        
        self.write_cmd(driver.CMD_CASET)    # set column XSTART/XEND
        self.write_data(bytearray(
            [0x00, xStart + self.margin_col, 0x00, xEnd + self.margin_col])
        )
        
        self.write_cmd(driver.CMD_RASET)    # set row XSTART/XEND
        self.write_data(bytearray(
            [0x00, yStart + self.margin_row, 0x00, yEnd + self.margin_row])
        )
        
        self.write_cmd(driver.CMD_RAMWR)    # write addresses to RAM
        

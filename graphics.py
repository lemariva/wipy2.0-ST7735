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

# MicroPython ST7735 LCD display driver

from driver import ST7735

class Display:             
    # screen size 
    LONG_EDGE_PIXELS = const(160)
    SHORT_EDGE_PIXELS = const(128)
    LCD_OFFSET_HEIGHT = const(0)
    LCD_OFFSET_WIDTH = const(0)      
        
    # colors
    COLOR_BLACK   = const(0x0000)
    COLOR_RED     = const(0x001F)
    COLOR_BLUE    = const(0xF800)
    COLOR_GREEN   = const(0x07E0)
    COLOR_CYAN    = const(0x07FF)
    COLOR_MAGENTA = const(0xF81F)
    COLOR_YELLOW  = const(0xFFE0)
    COLOR_WHITE   = const(0xFFFF)       
    
    def __init__(self, uSPI=0, pinDC='P7', pinCS='P8', pinRST='P6', bl=None, width=LONG_EDGE_PIXELS, height=SHORT_EDGE_PIXELS):       
        self.width        = width
        self.height       = height
        self.power_on     = True
        self.inverted     = False
        self.backlight_on = True
    
        # set column and row margins
        self.margin_row = 1
        self.margin_col = 2               
        
        # initializing driver 
        self.display = ST7735(uSPI, pinDC, pinCS, pinRST, bl)
        self.display.init()        
    
    def getScreenWidth(self):
        if (self.display._orientation == 0 or self.display._orientation == 2):
            return SHORT_EDGE_PIXELS
        else:
            return LONG_EDGE_PIXELS
    
    def getScreenHeight(self):
        if (self.display._orientation == 0 or self.display._orientation == 2):
            return LONG_EDGE_PIXELS
        else:
            return SHORT_EDGE_PIXELS               
    
    
    def invertColors(self, state=None):
        """
        Get/set display color inversion.
        """
        if state is None:
            return self.inverted
        self.display.write_cmd(driver.CMD_INVON if state else driver.CMD_INVOFF)
        self.inverted = state
    
    def rgbColor(self, r, g, b):
        """
        Pack 24-bit RGB into 16-bit value.
        """
        return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)      
    
    def clearScreen(self, color=COLOR_BLACK):
        """
        Clear the display filling it with color.
        """        
        w = self.getScreenWidth()
        h = self.getScreenHeight()
            
        self.display.setArea(0, 0, w - self.margin_row, h - self.margin_col)      
        self.fillRect(0, 0, w, h, color)
    
    def drawPixel(self, x, y, color):
        """
        Draw a single pixel on the display with given color.
        """
        self.display.setArea(x, y, x + 1, y + 1)
        self.display.write_pixels(1, bytearray([color >> 8, color]))
    
    
    def drawRect(self, xStart, yStart, xWidth, yHeight, color):
        """
        Draw a rectangle with specified coordinates/size
        """
        self.drawLine(xStart, xStart + xWidth, yStart, yStart, color)
        self.drawLine(xStart + xWidth, xStart + xWidth, yStart, yStart + yHeight, color)
    
        self.drawLine(xStart, xStart, yStart, yStart + yHeight, color)
        self.drawLine(xStart, xStart + xWidth, yStart + yHeight, yStart + yHeight, color)                        
        
        
    def fillRect(self, xStart, yStart, xWidth, yHeight, color):
        """
        Fill with color a rectangle with specified coordinates/size
        """
        # check the coordinates and trim if necessary
        if (xStart >= self.width) or (yStart >= self.height):
            return
        if (xStart + xWidth - 1) >= self.width:
            xWidth = self.width - xStart
        if (yStart + yHeight - 1) >= self.height:
            yHeight = self.height - yStart
    
        self.display.setArea(xStart, yStart, xStart + xWidth - 1, yStart + yHeight - 1)
        self.display.write_pixels((xWidth*yHeight), bytearray([color >> 8, color]))        
    
    
    def drawCircle(self, x, y, radius, color):
        """
        Draw a circle with specified coordinates and radius
        """        
        dx = radius
        dy = 0
        xChange = 1 - 2 * radius
        yChange = 1
        radiusError = 0
        while (dx >= dy):
            self.drawPixel(x + dx, y + dy, color)
            self.drawPixel(x - dx, y + dy, color)
            self.drawPixel(x - dx, y - dy, color)
            self.drawPixel(x + dx, y - dy, color)
            self.drawPixel(x + dy, y + dx, color)
            self.drawPixel(x - dy, y + dx, color)
            self.drawPixel(x - dy, y - dx, color)
            self.drawPixel(x + dy, y - dx, color)
            dy = dy + 1
            radiusError += yChange
            yChange += 2
            if (2 * radiusError + xChange > 0):
                dx = dx - 1
                radiusError += xChange
                xChange += 2
    
    def fillCircle(self, x, y, radius, color):     
        """
        Fill a circle with specified coordinates and radius
        """           
        dx = radius
        dy = 0
        xChange = 1 - 2 * radius
        yChange = 1
        radiusError = 0
        while (dx >= dy):
            self.drawLine(x + dy, y + dx, x - dy, y + dx, color)
            self.drawLine(x - dy, y - dx, x + dy, y - dx, color)
            self.drawLine(x - dx, y + dy, x + dx, y + dy, color)
            self.drawLine(x - dx, y - dy, x + dx, y - dy, color)
            dy = dy + 1
            radiusError += yChange
            yChange += 2;
            if (2 * radiusError + xChange > 0):
                dx = dx - 1
                radiusError += xChange
                xChange += 2
                      
    
    
    def drawString(self, x, y, string, font, color, size=1):
        """
        Draw text at a given position using the user font.
        Font can be scaled with the size parameter.
        """
        if font is None:
            return
    
        width = size * font['width'] + 1
    
        px = x
        for c in string:
            self.drawChar(px, y, c, font, color, size, size)
            px += width
    
            # wrap the text to the next line if it reaches the end
            if px + width > self.width:
                y += font['height'] * size + 1
                px = x
    
                
    def drawChar(self, x, y, char, font, color, sizex=1, sizey=1):
        """
        Draw a character at a given position using the user font.
        Font is a data dictionary, can be scaled with sizex and sizey.
        """
        if font is None:
            return
    
        startchar = font['start']
        endchar = font['end']
        ci = ord(char)
    
        if (startchar <= ci <= endchar):
            width = font['width']
            height = font['height']
            ci = (ci - startchar) * width
    
            ch = font['data'][ci:ci + width]
    
            # no font scaling
            px = x
            if (sizex <= 1 and sizey <= 1):
                for c in ch:
                    py = y
                    for _ in range(height):
                        if c & 0x01:
                            self.drawPixel(px, py, color)
                        py += 1
                        c >>= 1
                    px += 1
    
            # scale to given sizes
            else:
                for c in ch:
                    py = y
                    for _ in range(height):
                        if c & 0x01:
                            self.fillRect(px, py, sizex, sizey, color)
                        py += sizey
                        c >>= 1
                    px += sizex
        else:
            # character not found in this font
            return
    
    
    def drawLine(self, xStart, xEnd, yStart, yEnd, color):
        """
        Draw a line between the given points
        """
        # line is vertical
        if xStart == xEnd:
            # use the smallest y
            start, end = (xEnd, yEnd) if yEnd < yStart else (xStart, yStart)
            self.drawVline(start, end, abs(yEnd - yStart) + 1, color)
    
        # line is horizontal
        elif yStart == yEnd:
            # use the smallest x
            start, end = (xEnd, yEnd) if xEnd < xStart else (xStart, yStart)
            self.drawHline(start, end, abs(xEnd - xStart) + 1, color)
    
        else:
            # Bresenham's algorithm
            dx = abs(xEnd - xStart)
            dy = abs(yEnd - yStart)
            inx = 1 if xEnd - xStart > 0 else -1
            iny = 1 if yEnd - yStart > 0 else -1
    
            # steep line
            if (dx >= dy):
                dy <<= 1
                e = dy - dx
                dx <<= 1
                while (xStart != xEnd):
                    # draw pixels
                    self.drawPixel(xStart, yStart, color)
                    if (e >= 0):
                        yStart += iny
                        e -= dx
                    e += dy
                    xStart += inx
    
            # not steep line
            else:
                dx <<= 1
                e = dx - dy
                dy <<= 1
                while(yStart != yEnd):
                    # draw pixels
                    self.drawPixel(xStart, yStart, color)
                    if (e >= 0):
                        xStart += inx
                        e -= dy
                    e += dx
                    yStart += iny
    
    def drawHline(self, x, y, w, color):
        if (x >= self.width) or (y >= self.height):
            return
        if (x + w - 1) >= self.width:
            w = self.width - x
    
        self.display.setArea(x, y, x + w - 1, y)
        self.display.write_pixels(x+w-1, bytearray([color >> 8, color]))
    
    def drawVline(self, x, y, h, color):
        if (x >= self.width) or (y >= self.height):
            return
        if (y + h -1) >= self.height:
            h = self.height - y
    
        self.display.setArea(x, y, x, y + h - 1)
        self.display.write_pixels(y+h-1, bytearray([color >> 8, color]))
        
  
                
                
                
                

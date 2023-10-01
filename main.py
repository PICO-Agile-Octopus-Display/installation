import network
import ntptime
import utime
import time
import collections
import urequests
from strptime import strptime
import json
import select
import sys

# Code for Mono LCD

import gfx_pack
from picographics import PicoGraphics, DISPLAY_INKY_PACK

class DisplayItem:
    LEFT=0
    CENTRE=1
    RIGHT=2
    
    def __init__(self, x, y, display, foreground, background, font, size, width, height,alignment):
        self.display = display
        self.x = x
        self.y = y
        self.foreground = foreground
        self.background = background
        self.font = font
        self.size = size
        self.width = width
        self.height = height
        self.alignment = alignment
        self.text_width = 0
        self.text_x = 0
        self.old_text = ""
        
    def do_display(self,text):
        if text == self.old_text:
            return False
        if self.text_width != 0:
            self.display.set_pen(self.background)
            self.display.rectangle(self.text_x,self.y,self.text_width,self.height)
        self.display.set_pen(self.foreground)
        self.display.set_font(self.font)
        self.text_width = self.display.measure_text(text,scale=self.size)
        if self.alignment == DisplayItem.CENTRE:
            self.text_x=round((self.width-self.text_width)/2)
        elif self.alignment == DisplayItem.LEFT:
            self.text_x=0
        elif self.alignment == DisplayItem.RIGHT:
            self.text_x=self.x+(self.width-self.text_width)
        self.display.text(text,self.text_x,self.y,scale=self.size)
        self.old_text = text
        return True


class PrintDisplay:
    
    def __init__(self, ctrl):
        self.ctrl = ctrl
        
    def do_status(self, status):
        print("Status:",status)
 
    def do_min(self, min):
        print("Min:",min)
 
    def do_max(self, max):
        print("Max:",max)
 
    def do_tariff(self, tariff):
        print("Tariff:", tariff)

    def do_clock(self, clock):
        print("Clock:",clock)
        
    def draw(self):
        pass
    
    def do_bars(self,bars,bars_length,start):
        print("Bars:",bars,"Length:",bars_length,"Start:",start)



class Display:

    DRAW_COL=0
    ERASE_COL=15
    FAINT_COL=2
    DOTTED_COL=14
    
    BAR_X=10
    BAR_Y=53
    BAR_AREA_WIDTH=96
    BAR_AREA_HEIGHT=25
    
    FONT="bitmap8"
    FONT_SIZE=2
    FONT_HEIGHT=16
    
    TARIFF_FONT="bitmap8"
    TARIFF_FONT_SIZE=4
    TARIFF_FONT_HEIGHT=32

    MIN_Y=78
    MAX_Y=22
    
    def __init__(self, ctrl, display):
        self.ctrl = ctrl
        self.display = display
        self.width, self.height = self.display.get_bounds()
        print("Width:",self.width,"Height:",self.height)
        self.display.set_pen(self.ERASE_COL)
        self.display.rectangle(0,0,self.width,self.height)
        self.status = DisplayItem(0,self.height-self.FONT_HEIGHT,self.display,self.DRAW_COL,self.ERASE_COL,self.FONT,self.FONT_SIZE,round(self.width/2),32,DisplayItem.LEFT)
        self.clock = DisplayItem(round(self.width/2),self.height-self.FONT_HEIGHT,self.display,self.DRAW_COL,self.ERASE_COL,self.FONT,self.FONT_SIZE,round(self.width/2),self.FONT_HEIGHT,DisplayItem.RIGHT)
        w = 25 # width of min and max
        self.min = DisplayItem(self.width-w,self.MIN_Y,self.display,self.DRAW_COL,self.ERASE_COL,self.FONT,self.FONT_SIZE,w,self.FONT_HEIGHT,DisplayItem.RIGHT)
        self.max = DisplayItem(self.width-w,self.MAX_Y,self.display,self.DRAW_COL,self.ERASE_COL,self.FONT,self.FONT_SIZE,w,self.FONT_HEIGHT,DisplayItem.RIGHT)
        self.tariff = DisplayItem(0,0,self.display,self.DRAW_COL,self.ERASE_COL,self.TARIFF_FONT,self.TARIFF_FONT_SIZE,self.width,self.TARIFF_FONT_HEIGHT,DisplayItem.CENTRE)
        self.oldBars=[None]*48
        self.old_start=-1
        self.display_dirty = True
        
    def do_status(self, status):
        if self.status.do_display(status):
            self.display_dirty = True
 
    def do_min(self, min):
        if self.min.do_display(min):
            self.display_dirty = True
 
    def do_max(self, max):
        if self.max.do_display(max):
            self.display_dirty = True
 
    def do_tariff(self, tariff):
        if self.tariff.do_display(tariff):
            self.display_dirty = True

    def do_clock(self, clock):
        if self.clock.do_display(clock):
            self.display_dirty = True
        
    def draw(self):
        if self.display_dirty:
            self.display.update()
            self.display_dirty=False
    
class InkDisplay(Display):
    
    DRAW_COL=0
    ERASE_COL=15
    FAINT_COL=14
    DOTTED_COL=4
    
    BAR_X=10
    BAR_Y=35
    BAR_AREA_WIDTH=270
    BAR_AREA_HEIGHT=65
    
    FONT="bitmap8"
    FONT_SIZE=2
    FONT_HEIGHT=16
    
    TARIFF_FONT="bitmap8"
    TARIFF_FONT_SIZE=4
    TARIFF_FONT_HEIGHT=32

    MIN_Y=85
    MAX_Y=22
    
    def __init__(self, ctrl):
        display = PicoGraphics(DISPLAY_INKY_PACK)
        super(InkDisplay,self).__init__(ctrl, display)
        
        
    def do_bars(self,bars,bars_length,start):
        if bars == self.oldBars and start == self.old_start :
            return
        for i in range(0,len(bars)):
            self.oldBars[i] = bars[i]
        self.old_start = start
        low = bars[0]
        high=bars[0]
        base_height = 0.1*self.BAR_AREA_HEIGHT
        available_height = self.BAR_AREA_HEIGHT-base_height
        bar_width = int(self.BAR_AREA_WIDTH/bars_length)
        displayed_width = bar_width*bars_length
        bars_indent = int((self.BAR_AREA_WIDTH-displayed_width)/2.0)
        self.display.set_pen(self.ERASE_COL)
        self.display.rectangle(self.BAR_X,self.BAR_Y,self.BAR_AREA_WIDTH,self.BAR_AREA_HEIGHT)
        for i in range(bars_length):
            if bars[i]==None:
                continue
            if bars[i]>high:
                high=bars[i]
            if bars[i]<low:
                low=bars[i]
        rng = high-low
        scale_y=available_height/rng
        for i in range(bars_length):
            if bars[i]==None: continue
            bar_x=self.BAR_X+bars_indent+i*bar_width
            bar_height=((bars[i]-low)*scale_y)+base_height
            bar_y=self.BAR_Y+(self.BAR_AREA_HEIGHT-bar_height)
            if i<start:
                ink=self.FAINT_COL
            else:
                if i%2==0:
                    ink=self.DRAW_COL
                else:
                    ink=self.DOTTED_COL
            self.display.set_pen(ink)
            self.display.rectangle(round(bar_x),round(bar_y),round(bar_width),round(bar_height))
        self.display_dirty = True

class GFXDisplay(Display):
    
    DRAW_COL=15
    ERASE_COL=0
    FAINT_COL=2
    DOTTED_COL=14

    BAR_X=10
    BAR_Y=53
    BAR_AREA_WIDTH=96
    BAR_AREA_HEIGHT=25
    
    FONT="bitmap8"
    FONT_SIZE=1
    FONT_HEIGHT=8
    
    TARIFF_FONT="bitmap8"
    TARIFF_FONT_SIZE=2
    TARIFF_FONT_HEIGHT=16

    MIN_Y=46
    MAX_Y=22
    
    def __init__(self, ctrl):
        self.board = gfx_pack.GfxPack()
        self.board.set_backlight(0,255,0)
        self.display = self.board.display
        super(InkDisplay,self).__init__(ctrl, self.display)
        
    def do_bars(self,bars,bars_length,start):
        if bars == self.oldBars and start == self.old_start :
            return
        for i in range(0,len(bars)):
            self.oldBars[i] = bars[i]
        self.old_start = start
        x=self.BAR_X
        y=self.BAR_Y
        width=self.BAR_AREA_WIDTH
        height=self.BAR_AREA_HEIGHT
        low = bars[0]
        high=bars[0]
        base_height = 0.1*height
        available_height = height-base_height
        bar_width = width/bars_length
        self.display.set_pen(self.ERASE_COL)
        self.display.rectangle(x,y-height,width,height)
        for i in range(bars_length):
            if bars[i]==None:
                continue
            if bars[i]>high:
                high=bars[i]
            if bars[i]<low:
                low=bars[i]
        rng = high-low
        scale_y=available_height/rng
        scale_x=width/bars_length
        for i in range(bars_length):
            if bars[i]==None: continue
            sx=x+i*scale_x
            sy=y
            ex=x+i*scale_x
            ey=y-(((bars[i]-low)*scale_y)+base_height)
            if i<start:
                ink=2
            else:
                if i%2==0:
                    ink=15
                else:
                    ink=14
            self.display.set_pen(ink)
            self.display.line(round(sx),round(sy),round(ex),round(ey))
        self.display_dirty = True

class Agile:
    
    def __init__(self, ctrl):
        self.ctrl = ctrl
        self.rates = None
        self.update_day = None

    def do_get_daily_rates(self,time_mgr):
        self.ctrl.display.do_status("Getting daily rates")
        self.ctrl.display.draw()
        t = time_mgr.time
        self.update_date = t[2]
        start_secs = time.mktime((t[0], t[1], t[2], 0, 0, 0, 0, 0, -1))
        end_secs = time.mktime((t[0], t[1], t[2]+1, 0, 0, 0, 0, 0, -1))
        if time_mgr.summer:
            start_secs = start_secs-3600
            end_secs = end_secs-3600
        s = time.localtime(start_secs)           
        e = time.localtime(end_secs)
        period = "period_from=%d-%02d-%02dT%02d:%02dZ&period_to=%d-%02d-%02dT%02d:%02dZ"% \
                 (s[0],s[1],s[2],s[3],s[4], \
                  e[0],e[1],e[2],e[3],e[4])
        url = self.ctrl.config.settings['AgileURL']['value']
        print("Request:",url+period)
        res = urequests.get(url+"?"+period)
        results = res.json()["results"]
        self.half_hour_prices = [None] * 48
        
        total_cost = 0
        reading_count = 0
        self.min_price = 1000
        self.max_price = 0

        for result in results:
            price = result["value_inc_vat"]
            valid_from = result["valid_from"]
            t = strptime(valid_from, "%Y-%m-%dT%H:%M:%SZ")
            start_secs = time.mktime((t[0], t[1], t[2], t[3], t[4], 0, 0, 0, -1))
            if time_mgr.summer:
                start_secs = start_secs+3600
            start = time.localtime(start_secs)
            offset = start[3]*2
            if start[4]==30:
                offset = offset+1
            self.half_hour_prices[offset]=price
            total_cost = total_cost+price
            reading_count = reading_count + 1
            if price > self.max_price:
                self.max_price = price
            if price < self.min_price:
                self.min_price = price
            
        self.mean_price = total_cost / reading_count
        self.ctrl.display.do_status("Done")
        self.ctrl.display.draw()
        
    def do_get_rate(self,time_mgr):
        t=time_mgr.time
        if t[2] != self.update_day:
            self.do_get_daily_rates(time_mgr)
            self.update_day = t[2]
        self.offset = t[3]*2
        if t[4]>=30:
             self.offset=self.offset+1
        return self.half_hour_prices[self.offset]

class Connection:
    
    def __init__(self, ctrl):
        self.ctrl=ctrl
        
    def do_connect(self, ssid, pwd):
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        if not self.wlan.isconnected():
            self.ctrl.display.do_status("Connecting WiFi")
            self.ctrl.display.draw()
            self.wlan.connect(ssid, pwd)
            try_count=0
            while not self.wlan.isconnected():
                time.sleep(0.1)
                self.ctrl.console.update()
                try_count = try_count + 1
                if try_count == 50:
                    return False;
        self.ctrl.display.do_status("Got WiFi")
        self.ctrl.display.draw()
        print('network config:', self.wlan.ifconfig())
        try:
            self.ctrl.display.do_status("Getting time")
            self.ctrl.display.draw()
            print("Local time before synchronization:%s" %str(time.localtime()))
            #make sure to have internet connection
            ntptime.settime()
            print("Local time after synchronization:%s" %str(time.localtime()))
        except:
            print("Error syncing time")
            return False
            
        return True
    
class Time_Manager:
    
    def __init__(self, ctrl):
        self.ctrl=ctrl

    def update_time(self):
        secs = time.time()
        t = time.localtime(secs)
        
        # Calculate the day of the week for March 31st
        march_31st_secs = time.mktime((t[0], 3, 31, 0, 0, 0, 0, 0, -1))
        march_31st_time = time.localtime(march_31st_secs)
        march_31st_day_of_week = march_31st_time[6]  # 0 = Monday, 6 = Sunday
        # index from Sunday
        days_to_subtract = (march_31st_day_of_week+1)%7
        bst_start_secs = utime.mktime((t[0], 3, 31 - days_to_subtract, 1, 0, 0, 0, 0, -1))
        #
        # Calculate the day of the week for October 31st
        oct_31st_secs = utime.mktime((t[0], 10, 31, 0, 0, 0, 0, 0, -1))
        oct_31st_time = time.localtime(oct_31st_secs)
        oct_31st_day_of_week = oct_31st_time[6]  # 0 = Monday, 6 = Sunday
        # index from Sunday
        days_to_subtract = (oct_31st_day_of_week+1)%7
        bst_end_secs = utime.mktime((t[0], 10, 31 - days_to_subtract, 1, 0, 0, 0, 0, -1))
        #
        if secs<bst_start_secs or secs>bst_end_secs:
            self.summer = False
            self.time = t
        else:
            self.summer = True
            self.time = time.localtime(secs+3600)

class Config:
    
    SETTINGS_FILENAME = "settings.json"
    
    DEFAULT_SETTINGS = '''
{
        "wifiSSID": {
            "name": "WiFi SSID",
            "desc": "Name of the SSID point for the network",
            "type": "text",
            "value": "",
            "order": 1
        },

        "wifiPWD": {
            "name": "WiFi Password",
            "desc": "WiFi password for the network",
            "type": "password",
            "value": "",
            "order": 2
        },

        "display": {
            "name": "Display type",
            "desc": "Type of display being used in the device",
            "type": "string",
            "value": "print",
            "values": ["print","e-ink","lcd"],
            "order": 3
        },

        "AgileURL": {
            "name": "Agile Octopus URL",
            "desc": "URL for the Agile Octopus price data",
            "type": "text",
            "value": "https://api.octopus.energy/v1/products/AGILE-FLEX-22-11-25/electricity-tariffs/E-1R-AGILE-FLEX-22-11-25-M/standard-unit-rates/",
            "order": 4
        }
}
'''
    def __init__(self):
        self.settings=None
        
    def reset(self):
        self.save_settings_JSON_to_file(self.DEFAULT_SETTINGS)
        self.settings = json.loads(self.DEFAULT_SETTINGS)
        
    def save_settings_JSON_to_file(self,settings_JSON):
        try:
            with open (self.SETTINGS_FILENAME,"w") as file:
                print("File write")
                content = file.write(settings_JSON)
                file.close()
        except OSError as e:
                print("File write error:", e)
                
    def save(self):
        self.save_settings_JSON_to_file(json.dumps(self.settings))
            
    def load(self):
        try:
            with open (self.SETTINGS_FILENAME,"r") as file:
                content = file.read()
                self.loadJSON(content)
                print("Settings loaded from file")
        except OSError as e:
            print("File not found:", e)
            self.reset()
            
    def getJSON(self):
        return json.dumps(self.settings)
    
    def loadJSON(self,content):
        try:
            self.settings = json.loads(content)
            self.save()
            return True
        except ValueError as e:
            print("Badly formed JSON settings", e)
            return False
        
    def get(self,name):
        return self.settings[name]['value']
    
    def put(self,name,value):
        self.settings[name]['value'] = value
        self.save()
        
class Console:
    
    def reset(self):
        self.buffer = ""
        
    def __init__(self, line_receiver):
        self.line_receiver = line_receiver
        self.reset()
        
    def update(self):
        while select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
            ch = sys.stdin.read(1)
            if ord(ch) == 10:
                # got a linefeed
                if len(self.buffer)>0:
                    self.line_receiver(self.buffer)
                self.reset()
            else:
                self.buffer = self.buffer + ch

class Manager:
    
    def line_receiver(self,line):
        if line == "*send":
            print("*",self.config.getJSON())
            return
           
        if line.startswith("*json "):
            print("got json")
            json = line[6:]
            if self.config.loadJSON(json):
                print("*done")
                time.sleep(2)
                machine.reset()
            else:
                print("*failed")
            
    def __init__(self):
        print("Agile Octopus Tariff Display")
        print("https://github.com/CrazyRobMiles/AgileOctopusPICODisplay")        
        self.config = Config()
        self.config.load()
        
    def do_console_loop(self):
        while True:
            self.console.update()
            time.sleep(0.01)
        
    def do_start(self):
        wifi_ssid = self.config.get('wifiSSID')
        wifi_pwd = self.config.get('wifiPWD')

        display_type = self.config.get('display')
        
        if display_type == "print":
            self.display = PrintDisplay(self)
        if display_type == "e-ink":
            self.display = InkDisplay(self)
        if display_type == "lcd":
            self.display = GFXDisplay(self)
        self.console = Console(self.line_receiver)

        if wifi_ssid=="":
            self.display.do_status("No WiFi settings - connect to USB")
            self.do_console_loop()
                
        self.display.do_status("Starting")
        self.display.draw()
        self.agile = Agile(self)
        self.connection = Connection(self)
        self.time_mgr = Time_Manager(self)
        self.display.do_status("Starting")
        self.display.draw()
        if not self.connection.do_connect(wifi_ssid,wifi_pwd):
            self.display.do_status("WiFi connnection failed")
            self.display.draw()
            self.do_console_loop()
        self.time_mgr.update_time()
        self.rate = self.agile.do_get_rate(self.time_mgr)
        
    def do_update(self):
        self.time_mgr.update_time()
        t = self.time_mgr.time
        self.display.do_clock("%2d:%02d"%(t[3],t[4]))
        self.rate = self.agile.do_get_rate(self.time_mgr)
        self.display.do_tariff("%.2f"%(self.rate))
        self.display.do_bars(self.agile.half_hour_prices,48, self.agile.offset)
        self.display.do_min("%.0f"%self.agile.min_price)
        self.display.do_max("%.0f"%self.agile.max_price)
        self.display.draw()
        self.console.update()
       
manager = Manager()
manager.do_start()
while True:
    manager.do_update()
    time.sleep(1)




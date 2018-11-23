# Import all the libraries we need to run
try: 
    import spidev
    useSpi = True
except:
    useSpi = False
import RPi.GPIO as GPIO
class hwio :
    def __init__ (self) :
        GPIO.setmode(GPIO.BOARD)
        # Open SELF.SPI bus
        self.useSpi = useSpi
        if(self.useSpi) :
            self.spi = spidev.SpiDev()
        else:
            self.spi = False
        self.adc = [adcChan(self.useSpi,self.spi,0,0,(4.096/4096.0)),
               adcChan(self.useSpi,self.spi,0,1,(4.096/4096.0)),
               adcChan(self.useSpi,self.spi,0,2,(4.096/4096.0)),
               adcChan(self.useSpi,self.spi,0,3,(4.096/4096.0)),
               adcChan(self.useSpi,self.spi,0,4,(4.096/4096.0)),
               adcChan(self.useSpi,self.spi,0,5,(4.096/4096.0)),
               adcChan(self.useSpi,self.spi,0,6,(4.096/4096.0)),
               adcChan(self.useSpi,self.spi,0,7,(4.096/4096.0))]
        self.adf = adfIf(self.useSpi,self.spi,1)

class adcChan :
    def __init__ (self,useSpi,spi,bus,chan,scale) :
        self.useSpi = useSpi
        self.spi = spi
        self.bus = bus
        self.chan = chan
        self.scale = scale
        if(chan > 7 or chan < 0) :
            print("Error bad adc channel number must be 0-7")
            return -1
    def measure(self) :
        if(self.useSpi) :
            self.spi.open(0,self.bus)
            self.spi.max_speed_hz=3000000
            r = self.spi.xfer2([1, 8 + self.chan << 4, 0])
            self.spi.close()
            data = ((r[1] & 3) << 8) + r[2]
            self.val = (float(data) * self.scale)
        else:
            self.val = -1
        return ( self.val )
class adfIf:
    def __init__ (self,useSpi,spi, bus) :
        self.useSpi = useSpi
        self.spi = spi
        self.bus = bus
    def writeVal(self,val32) :
        v = [((val32>>24) & 0xff),((val32>>16) & 0xff),((val32>>8) & 0xff),(val32 & 0xff)]
        r = val32 & 0x7
        print("r %d = %02x %02x %02x %02x" % (r, v[0], v[1], v[2], v[3]))
        if(self.useSpi) :
            self.spi.open(0,self.bus)
            self.spi.max_speed_hz=1000000
            r = self.spi.xfer2(v)
            self.spi.close()

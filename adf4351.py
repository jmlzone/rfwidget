#import math
try: 
    import spidev
    useSpi = True
except:
    useSpi = False

class adf4351 :
    def __init__ (self) :
        self.INT_N = 0
        self.FRAC_F = 0
        self.PHASE_ADJ = 0
        self.PRESCALAR = 0
        self.PHASE_P = 1
        self.MODULUS_M = 0
        self.LN_LS = 3
        self.MUX = 0
        self.DBR_RD = 0
        self.DBR_R = 10
        self.DUB_BUF = 0
        self.CHG_PUMP = 7
        self.LDF = 0
        self.LPD = 0
        self.PD_POL = 1
        self.PWR_DN = 0
        self.CP_TS = 0
        self.CNTR_RST = 0
        self.BSCM = 0
        self.ABP = 0
        self.CHG_CAN = 0
        self.CSR = 0
        self.CLK_DIV_MODE = 0
        self.CLK_DIV_VAL = 150
        self.FB_SEL = 0
        self.RF_DIV_SEL = 0
        self.BAND_SEL_CLK_DIV = 0
        self.VCO_PD = 0
        self.MTLD = 1
        self.AUX_SEL = 0
        self.AUX_EN = 0
        self.AUX_PWR = 0
        self.RF_EN = 0
        self.RF_PWR = 0
        self.LD_MODE = 1
        self.refclk = 25.0 #MHz
        self.channelSpacing = 5.0 #KHz
        self.calcFreq = 0

    def formRegs(self) :
        self.R0 = ((self.INT_N & 0xffff) << 15) + ((self.FRAC_F & 0xfff) <<3)
        self.R1 = ((self.PHASE_ADJ<<28) + (self.PRESCALAR<<27)
        + ((self.PHASE_P & 0xfff)<<15)
        + ((self.MODULUS_M & 0xfff)<<3) + 1)
        self.R2 = ((self.LN_LS << 29) + (self.MUX << 26) + (self.DBR_RD <<24)
        + ((self.DBR_R & 0x3ff) <<14) + (self.DUB_BUF<<13)
        + ((self.CHG_PUMP & 0xf) << 9) + (self.LDF<<8)
        + (self.LPD<<7) + (self.PD_POL<<6) + (self.PWR_DN<<5)
        + (self.CP_TS<<4) + (self.CNTR_RST<<3) + 2)
        self.R3 = ((self.BSCM<<23) + (self.ABP<<22) + (self.CHG_CAN<<21)
        + (self.CSR<<18) + (self.CLK_DIV_MODE<<15)
        + ((self.CLK_DIV_VAL & 0xfff) <<3) + 3)
        self.R4 = ((self.FB_SEL<<23) + (self.RF_DIV_SEL<<20)
        + (self.BAND_SEL_CLK_DIV<<12)
        + (self.VCO_PD<<11) + (self.MTLD<<10) + (self.AUX_SEL<<9)
        + (self.AUX_EN<<8) + (self.AUX_PWR<<6) + (self.RF_EN<<5)
        + (self.RF_PWR<<3) +  4)
        self.R5 = (self.LD_MODE<<22) + (3 << 19) + 5
        print("r5 = %08x" % self.R5);
        print("r4 = %08x" % self.R4);
        print("r3 = %08x" % self.R3);
        print("r2 = %08x" % self.R2);
        print("r1 = %08x" % self.R1);
        print("r0 = %08x" % self.R0);

    """ from MainForm.cs sample code on the analog divices web site
        https://ez.analog.com/thread/13743
    """
    def setFreq(self,freq) :
        if((freq <34.375) or (freq >4400)) :
            print("frequency must be between 34.375MHz & 4400 MHz %f is not" % freq)
            return(False)
        
        self.RF_DIV_SEL = 0
        if(self.DBR_RD &2) : # double
            doubleHalf = 2.0
        else :
            doubleHalf = 1.0
        if(self.DBR_RD &1) : # half
            doubleHalf = doubleHalf/2.0
        pfdFreq = self.refclk * doubleHalf / self.DBR_R
        fband = 2200.0
        while(float(fband) > float(freq)) :
            self.RF_DIV_SEL = self.RF_DIV_SEL + 1
            fband = fband / 2.0
        if(self.FB_SEL) :
            N = freq * (2**self.RF_DIV_SEL) / pfdFreq
        else:
            N = freq / pfdFreq
        INT = int(N)
        MOD = int(round((1000.0*pfdFreq)/self.channelSpacing))
        FRAC = int(round((N-INT) * MOD))

        GCD = int(self.gcd(MOD,FRAC)) # greatest common devisor
        print("pfdFreq= %f" %pfdFreq)
        print("N= %f" %N)
        print("freq= %f" %freq)
        print("fband= %f" %fband)
        print("rfDivSel= %d" %self.RF_DIV_SEL)
        print("INT= %d" %INT)
        print("MOD= %d" %MOD)
        print("FRAC= %d" %FRAC)
        print("GCD= %d" %GCD)
        
        self.MODULUS_M = int(MOD/GCD)
        if(self.MODULUS_M ==1 ) :
             self.MODULUS_M =2
        self.FRAC_F = int(FRAC/GCD)
        self.INT_N = INT
        ####self.
        self.checkValues()
        # base select clock
        temp = round(pfdFreq * 8)
        if(((8.0 * pfdFreq) - temp) > 0) :
            temp = temp + 1
        if(temp > 255) :
            temp=255
        self.BAND_SEL_CLK_DIV = int(temp)
        self.calcFreq = ((float(INT) + float(float(FRAC) / float(MOD))) * float(pfdFreq))
        print("calculated frequency %f" % self.calcFreq)
        
    #def setLvl(self,lvl) :
    #def setPhase(self,phase) :
    #    self.PHASE

    def gcd(self, x, y): 
        while(y): 
            x, y = y, x % y 
        return x 
    
    def checkValues(self) :
        errors = ""
        ok = 1
        if(self.INT_N < 23) :
            ok = 0
            errors = errors + ("N must be greater than 23, was %d\n" % self.INT_N)
        if(self.INT_N > 65535) :
            ok = 0
            errors = errors + ("N must be less than 65535, was %d\n" % self.INT_N)
        if(self.FRAC_F > 4095) :
            ok = 0
            errors = errors + ("FRAC must be less than 4095, was %d\n" % self.FRAC_F)
        if(self.MODULUS_M < 2) :
            ok = 0
            errors = errors + ("MOD must be 2 or greater, was %d\n" % self.MODULUS_M)
        if(self.MODULUS_M > 4095) :
            ok = 0
            errors = errors + ("MOD must be less than 4095, was %d\n" % self.MODULUS_M)
        if(self.MODULUS_M < 2) :
            ok = 0
            errors = errors + ("MOD must be 2 or greater, was %d\n" % self.MODULUS_M)
        if(self.MODULUS_M > 4095) :
            ok = 0
            errors = errors + ("MOD must be less than 4095, was %d\n" % self.MODULUS_M)
        if(self.DBR_R < 1) :
            ok = 0
            errors = errors + ("R must be 1 or greater, was %d\n" % self.DBR_R)
        if(self.DBR_R > 1023) :
            ok = 0
            errors = errors + ("R must be less than 1023, was %d\n" % self.DBR_R)
        if(not ok) :
            print(errors)


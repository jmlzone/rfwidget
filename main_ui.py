#!/usr/bin/python
import wx
import adf4351
import hwio

# Define the tab content as classes:
 
class CWMode(wx.Panel):
    def __init__(self, parent,pll,hwio):
        wx.Panel.__init__(self, parent)
        self.pll=pll
        self.hwio=hwio
        #t = wx.StaticText(self, -1, "This is the second tab", (20,20))
        vbox = wx.BoxSizer(wx.VERTICAL) 
        hbox1 = wx.BoxSizer(wx.HORIZONTAL) 
        l1 = wx.StaticText(self, -1, "Enter Frequency")
        mhz = wx.StaticText(self, -1, "MHz")
        khz = wx.StaticText(self, -1, "KHz")
        hbox1.Add(l1, 1, wx.EXPAND|wx.ALIGN_RIGHT|wx.ALL,5) 
        self.freq = wx.TextCtrl(self,style=wx.TE_PROCESS_ENTER|wx.TE_RIGHT,value="224.080")  
        self.freq.Bind(wx.EVT_TEXT_ENTER,self.EnterFrequencyCB)  
        hbox1.Add(self.freq,1,wx.EXPAND|wx.ALIGN_RIGHT|wx.ALL,5) 
        #hbox1.Add(mhz, 1, wx.EXPAND|wx.ALIGN_LEFT|wx.ALL,5) 
        self.rfEn = wx.CheckBox(self,label="RF Enable")
        self.rfEn.Bind(wx.EVT_CHECKBOX,self.rfEnableCB)  
        hbox1.Add(self.rfEn,1,wx.EXPAND|wx.ALIGN_RIGHT|wx.ALL,5) 
        vbox.Add(hbox1)

        hboxref = wx.BoxSizer(wx.HORIZONTAL) 
        lr = wx.StaticText(self, -1, "R Counter")
        hboxref.Add(lr, 1, wx.EXPAND|wx.ALIGN_RIGHT|wx.ALL,5) 
        self.r = wx.TextCtrl(self,style=wx.TE_PROCESS_ENTER|wx.TE_RIGHT,value=("%d" % self.pll.DBR_R))  
        self.r.Bind(wx.EVT_TEXT_ENTER,self.EnterRcountCB)  
        hboxref.Add(self.r,1,wx.EXPAND|wx.ALIGN_RIGHT|wx.ALL,5) 
        self.dbl = wx.CheckBox(self,label="Double")
        self.dbl.SetValue(((self.pll.DBR_RD>>1) & 0x1))
        self.dbl.Bind(wx.EVT_CHECKBOX,self.dblHalfCB)  
        hboxref.Add(self.dbl,1,wx.EXPAND|wx.ALIGN_RIGHT|wx.ALL,5) 
        self.half = wx.CheckBox(self,label="Half")
        self.dbl.SetValue((self.pll.DBR_RD & 0x1))
        self.half.Bind(wx.EVT_CHECKBOX,self.dblHalfCB)  
        hboxref.Add(self.half,1,wx.EXPAND|wx.ALIGN_RIGHT|wx.ALL,5) 
        vbox.Add(hboxref)
        
        hbox2 = wx.BoxSizer(wx.HORIZONTAL) 
        l2 = wx.StaticText(self, -1, "Calculated Frequency") 
        hbox2.Add(l2, 1, wx.EXPAND|wx.ALIGN_RIGHT|wx.ALL,5) 
        self.calcFreq = wx.TextCtrl(self, value = "",style = wx.TE_READONLY|wx.TE_RIGHT) 
        hbox2.Add(self.calcFreq,1,wx.EXPAND|wx.ALIGN_RIGHT|wx.ALL,5) 
        hbox2.Add(mhz, 1, wx.EXPAND|wx.ALIGN_LEFT|wx.ALL,5) 
        vbox.Add(hbox2)
        
        #hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        #l3 = wx.StaticText(self, -1, "RF Enable")
        #hbox3.Add(l3, 1, wx.EXPAND|wx.ALIGN_RIGHT|wx.ALL,5)
        #self.c3 = wx.CheckBox(self,label="RF Enable")
        #self.c3.Bind(wx.EVT_CHECKBOX,self.rfEnableCB)  
        #hbox3.Add(self.c3,1,wx.EXPAND|wx.ALIGN_RIGHT|wx.ALL,5) 
        #vbox.Add(hbox3)

        hbox4  = wx.BoxSizer(wx.HORIZONTAL)
        l4 = wx.StaticText(self, -1, "RF Level")
        hbox4.Add(l4, 1, wx.EXPAND|wx.ALIGN_RIGHT|wx.ALL,5)
        self.rfPwr = wx.ComboBox(self,choices=['-4','-1','+2','+5'])
        self.rfPwr.SetSelection(self.pll.RF_PWR)
        self.rfPwr.Bind(wx.EVT_COMBOBOX,self.rfLevelCB)  
        hbox4.Add(self.rfPwr,1,wx.EXPAND|wx.ALIGN_RIGHT|wx.ALL,5) 
        lcpc = wx.StaticText(self, -1, "Charge Pump Current")
        hbox4.Add(lcpc, 1, wx.EXPAND|wx.ALIGN_RIGHT|wx.ALL,5)
        self.cpc = wx.ComboBox(self,choices=['0.31','0.63','0.94','1.25',
                                             '1.56','1.88','2.19','2.50',
                                              '2.81','3.13','3.44','3.75',
                                              '4.06','4.38','4.69','5.00'])
        self.cpc.SetSelection(self.pll.CHG_PUMP)
        self.cpc.Bind(wx.EVT_COMBOBOX,self.cpcCB)  
        hbox4.Add(self.cpc,1,wx.EXPAND|wx.ALIGN_RIGHT|wx.ALL,5) 
        vbox.Add(hbox4)

        hbox5  = wx.BoxSizer(wx.HORIZONTAL)
        l5 = wx.StaticText(self, -1, "Channel Spacing")
        hbox5.Add(l5, 1, wx.EXPAND|wx.ALIGN_RIGHT|wx.ALL,5)
        self.chspace = wx.TextCtrl(self,style=wx.TE_PROCESS_ENTER|wx.TE_RIGHT,value=("%0.1f" %self.pll.channelSpacing))  
        self.chspace.Bind(wx.EVT_TEXT_ENTER,self.ChannelSpacingCB)  
        hbox5.Add(self.chspace,1,wx.EXPAND|wx.ALIGN_RIGHT|wx.ALL,5) 
        hbox5.Add(khz, 1, wx.EXPAND|wx.ALIGN_LEFT|wx.ALL,5) 
        vbox.Add(hbox5)


        self.SetSizer(vbox) 
        self.Centre() 
        self.Show() 
        self.Fit()  

    def EnterFrequencyCB(self,event): 
        val = event.GetString() 
        print("Frequency Entered '%s'" % val)
        self.calcFreqSetRegs()

    def ChannelSpacingCB(self,event) :
        val = event.GetString() 
        print("Channel Spacing Entered '%s'" % val)
        self.pll.channelSpacing = float(val)
        self.calcFreqSetRegs()
        
    def calcFreqSetRegs(self) :
        val = self.freq.GetValue() 
        f = float(val)
        self.pll.setFreq(f)
        self.calcFreq.SetValue("%f" % pll.calcFreq)
        self.pll.formRegs()
        self.hwio.adf.writeVal(self.pll.R5)
        self.hwio.adf.writeVal(self.pll.R4)
        self.hwio.adf.writeVal(self.pll.R3)
        self.hwio.adf.writeVal(self.pll.R2)
        self.hwio.adf.writeVal(self.pll.R1)
        self.hwio.adf.writeVal(self.pll.R0)
        print("adc0 = %f v" % self.hwio.adc[0].measure())
        print("adc1 = %f v" % self.hwio.adc[1].measure())
        print("adc2 = %f v" % self.hwio.adc[2].measure())

    def rfEnableCB(self,event):
        val = self.rfEn.GetValue()
        print("RF enable changed: '%d'" % val)
        self.pll.RF_EN = val
        self.calcFreqSetRegs()

    def rfLevelCB(self,event):
        val = self.rfPwr.GetSelection()
        print("RF Level changed: '%d'" % val)
        self.pll.RF_PWR = val
        self.calcFreqSetRegs()

    def cpcCB(self,event):
        val = self.cpc.GetSelection()
        print("ChargePump Current changed: '%d'" % val)
        self.pll.CHG_PUMP = val
        self.calcFreqSetRegs()

    def EnterRcountCB(self,event):
        val=self.r.GetValue()
        self.pll.DBR_R=int(val)
        print("R changed: '%d'" % self.pll.DBR_R)

    def dblHalfCB(self,event) :
        dbl = self.dbl.GetValue()
        half = self.half.GetValue()
        val = (dbl*2) + half
        self.pll.DBR_RD = val
        print("dbl half changed: '%d'" % val)
        
class TabTwo(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        t = wx.StaticText(self, -1, "This is the Second tab", (20,20))

class TabThree(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        #t = wx.StaticText(self, -1, "This is the third tab", (20,20))
        vbox = wx.BoxSizer(wx.VERTICAL) 
         
        hbox1 = wx.BoxSizer(wx.HORIZONTAL) 
        l1 = wx.StaticText(self, -1, "Text Field") 
		
        hbox1.Add(l1, 1, wx.EXPAND|wx.ALIGN_LEFT|wx.ALL,5) 
        self.t1 = wx.TextCtrl(self,style=wx.TE_PROCESS_ENTER) 
		
        hbox1.Add(self.t1,1,wx.EXPAND|wx.ALIGN_LEFT|wx.ALL,5) 
        self.t1.Bind(wx.EVT_TEXT_ENTER,self.OnEnterPressed)  
        vbox.Add(hbox1) 
		
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        l2 = wx.StaticText(self, -1, "password field") 
		
        hbox2.Add(l2, 1, wx.ALIGN_LEFT|wx.ALL,5) 
        self.t2 = wx.TextCtrl(self,style = wx.TE_PASSWORD) 
        self.t2.SetMaxLength(5) 
		
        hbox2.Add(self.t2,1,wx.EXPAND|wx.ALIGN_LEFT|wx.ALL,5) 
        vbox.Add(hbox2) 
        self.t2.Bind(wx.EVT_TEXT_MAXLEN,self.OnMaxLen)
		
        hbox3 = wx.BoxSizer(wx.HORIZONTAL) 
        l3 = wx.StaticText(self, -1, "Multiline Text") 
		
        hbox3.Add(l3,1, wx.EXPAND|wx.ALIGN_LEFT|wx.ALL,5) 
        self.t3 = wx.TextCtrl(self,size = (200,100),style=wx.TE_MULTILINE|wx.TE_PROCESS_ENTER) 
		
        hbox3.Add(self.t3,1,wx.EXPAND|wx.ALIGN_LEFT|wx.ALL,5) 
        vbox.Add(hbox3) 
        self.t3.Bind(wx.EVT_TEXT_ENTER,self.OnEnterPressed)  
		
        hbox4 = wx.BoxSizer(wx.HORIZONTAL) 
        l4 = wx.StaticText(self, -1, "Read only text") 
		
        hbox4.Add(l4, 1, wx.EXPAND|wx.ALIGN_LEFT|wx.ALL,5) 
        self.t4 = wx.TextCtrl(self, value = "ReadOnly Text",style = wx.TE_READONLY|wx.TE_CENTER) 
			
        hbox4.Add(self.t4,1,wx.EXPAND|wx.ALIGN_LEFT|wx.ALL,5) 
        vbox.Add(hbox4) 
        self.SetSizer(vbox) 
        
        self.Centre() 
        self.Show() 
        self.Fit()  
		
    def OnKeyTyped(self, event): 
        print(event.GetString() )
		
    def OnEnterPressed(self,event): 
        val = event.GetString() 
        print("Enter pressed got '%s'" % val)
        self.t4.SetValue(val)
		
    def OnMaxLen(self,event): 
        print("Maximum length reached")

 
class TabFour(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        t = wx.StaticText(self, -1, "This is the last tab", (20,20))
 
 
class MainFrame(wx.Frame):
    def __init__(self,pll,hwio):
        wx.Frame.__init__(self, None, title="wxPython tabs example @pythonspot.com")
 
        # Create a panel and notebook (tabs holder)
        p = wx.Panel(self)
        nb = wx.Notebook(p)
 
        # Create the tab windows
        cwmode = CWMode(nb,pll,hwio)
        tab1 = TabTwo(nb)
        tab3 = TabThree(nb)
        tab4 = TabFour(nb)
 
        # Add the windows to tabs and name them.
        nb.AddPage(cwmode, "CW Mode")
        nb.AddPage(tab1, "Tab 2")
        nb.AddPage(tab3, "Tab 3")
        nb.AddPage(tab4, "Tab 4")
 
        # Set noteboook in a sizer to create the layout
        sizer = wx.BoxSizer()
        sizer.Add(nb, 1, wx.EXPAND)
        p.SetSizer(sizer)

        # Setting up the menu.
        filemenu= wx.Menu()
        filemenu.Append(101, "Open", "Open")
        filemenu.Append(102, "Save", "Save")
        filemenu.Append(wx.ID_ABOUT, "About","About")
        filemenu.Append(wx.ID_EXIT,"Exit","Close")
 
        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,"File") # Adding the "filemenu" to the MenuBar
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.

 
 
if __name__ == "__main__":
    app = wx.App()
    pll=adf4351.adf4351()
    hwio=hwio.hwio()
    MainFrame(pll,hwio).Show()
    app.MainLoop()

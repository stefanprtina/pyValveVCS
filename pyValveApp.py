import tkinter as tk
import time
import sys
from timeit import default_timer as timer
import serial
import serial.tools.list_ports
import matplotlib.pyplot as plt
import os
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.offsetbox import AnchoredText
import numpy as np
from shutil import copyfile
from fpdf import FPDF


class pyValveApp(tk.Frame):
    def __init__(self, parent):

        self.parent = parent

        # Status bar
        self.statusBar = StatusBar(self.parent)
        self.statusBar.pack(side="bottom", fill="x")

        self.glavniMeni = MenuClass(self.parent)
        self.ani = " "


        self.serialInst = serialCom()

        fontBold = "helvetica 14 bold"
        fontRegular = "helvetica 13"

        parent.title("pyValve v0.2")
        self.frame = tk.Frame(self.parent)
        labelPodaci = tk.Label(self.parent, text="Osnovni podaci o ventilu",font=fontBold)
        labelPodaci.place(x=20, y=10)

        #Lokacija ventila
        labelLokacijaVentila = tk.Label(self.parent, text="Lokacija ventila:", bd=1, font=fontRegular)
        labelLokacijaVentila.place(x=30, y=55)

        self.entryLokacijaVentila = tk.Entry(self.parent)
        self.entryLokacijaVentila.place(x=150, y=50)

        #Serijski broj
        labelSerBrojVentila = tk.Label(self.parent, text="Serijski broj:", bd=1, font=fontRegular)
        labelSerBrojVentila.place(x=30, y=85)
        self.entrySerBrojVentila = tk.Entry(self.parent)
        self.entrySerBrojVentila.place(x=150, y=80)

        #Nominalni precnik
        labelPrecnikVentila = tk.Label(self.parent, text="Nominalni prečnik:", font=fontRegular)
        labelPrecnikVentila.place(x=30, y=115)

        self.entryPrecnikVentila = tk.Entry(self.parent)
        self.entryPrecnikVentila.place(x=150, y=110)

        #Radni medijum
        labelRadniMedijVentila = tk.Label(self.parent, text="Radni medijum:", font=fontRegular)
        labelRadniMedijVentila.place(x=30, y=145)

        self.entryRadniMedijVentila = tk.Entry(self.parent)
        self.entryRadniMedijVentila.place(x=150, y=140)

        labelIspitniPodaci = tk.Label(self.parent, text="Ispitni podaci", font=fontBold)
        labelIspitniPodaci.place(x=30, y=180)

        #Pritisak početka otvaranja

        labelPritisakOtvaranja = tk.Label(self.parent, text="Pritisak otvaranja:", font=fontRegular)
        labelPritisakOtvaranja.place(x=30, y=215)

        self.entryPritisakOtvaranja = tk.Entry(self.parent)
        self.entryPritisakOtvaranja.place(x=150, y=210)

        #Ispitni medijum
        labelRadniMedijVentila = tk.Label(self.parent, text="Ispitni medijum:", font=fontRegular)
        labelRadniMedijVentila.place(x=30, y=245)

        self.radniMedijVar = tk.StringVar(self.parent)
        self.radniMedijList = ["N2", "Voda"]
        self.radniMedijVar.set(self.radniMedijList[0])

        self.selRadniMedijVentila = tk.OptionMenu(self.parent, self.radniMedijVar, *self.radniMedijList)
        self.selRadniMedijVentila.place(x=150, y=240)

        #Port selection

        #label
        labelPortSel = tk.Label(self.parent, text="Interfejs senzora", font=fontBold)
        labelPortSel.place(x=420, y=10)

        #Serijski port
        self.labelSerPort = tk.Label(self.parent, text="Izaberi port", font=fontRegular)
        self.labelSerPort.place(x=420, y=40)

        self.serPortVar = tk.StringVar(self.parent)
        self.serPortList = [port.device for port in self.serialInst.getPorts()]

        if(self.serPortList):
            self.serPortVar.set(self.serPortList[0])
        self.selSerPort = tk.OptionMenu(self.parent, self.serPortVar, *self.serPortList)
        self.selSerPort.place(x=420, y=70)

        self.buttonOpenSerial = tk.Button(text="Konektuj interfejs", command=lambda: self.serialInst.open(self.buttonOpenSerial, self.serPortVar.get()))
        self.buttonOpenSerial.place(x=470, y=100)


        labelSerPort = tk.Label(self.parent, text="Izaberi mjerno područje transmitera(bar)", font=fontRegular)
        labelSerPort.place(x=420, y=160)
        self.sensRangeVar = tk.StringVar(self.parent)
        self.sensRangeList = [10, 25, 100, 200, 300, 500]
        self.sensRangeVar.set(self.sensRangeList[0])
        sensRangeMenu = tk.OptionMenu(self.parent, self.sensRangeVar, *self.sensRangeList)
        self.sensRangeVar.trace('w', lambda *args: self.sensRangeUpdate())
        sensRangeMenu.place(x=470, y=190)

        #Setup dijagrama

        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(1, 1, 1)
        self.ax.set_ylim(0, int(self.sensRangeVar.get())*1.2)
        self.ax.set_xlim(0, 10)
        self.xs = []
        self.ys = []
        plt.subplots_adjust(bottom=0.30)
        plt.grid()
        plt.title('Dijagram ispitivanja ventila sigurnosti')
        plt.ylabel('Pritisak (bar)')
        plt.xlabel('Vrijeme (s)')

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.parent)  # A tk.DrawingArea.
        self.canvas.draw()
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.parent)
        self.toolbar.update()
        self.canvas.get_tk_widget().place(x=20, y=280)

        self.buttonDijagram = tk.Button(text="Počni ispitivanje", command=self.animationStart)
        self.buttonDijagram.place(x=470, y=240)

        self.buttonDijagram = tk.Button(text="Završi ispitivanje", command=self.animationStop)
        self.buttonDijagram.place(x=470, y=270)

    def animate(self, i, xs, ys):

        starttime = timer()
        xs = self.xs
        ys = self.ys

        if(ys):
            ymax = max(self.ys)
            print(ymax)

        mappedVal = np.interp(self.serialInst.getData(), [0.0, 1023.0], [0.0, float(self.sensRangeVar.get())])
        if(self.xs):
            self.xs.append(xs[-1]+0.05)
            xlim = self.ax.get_xlim()
            if(max(self.xs) > max(self.ax.get_xlim())):
              self.ax.set_xlim(0, (max(self.ax.get_xlim())+2))

        else:
            self.xs = [0.05]

        self.ys.append(mappedVal)

        # Limit x and y lists to 20 items
        #self.xs = self.xs[-20:]
        #self.ys = self.ys[-20:]


        text= "P = " + str(mappedVal)[:4] + ", Pmax = "+str(max(self.ys))[:4]
        paramBox = AnchoredText(text, loc=2)

        #Obrisi stari parambox
        if(self.paramBoxBuff):
            self.paramBoxBuff.remove()
        #---------------------------

        # Nacrtaj parambox
        self.paramBoxBuff = self.ax.add_artist(paramBox)

        # Nacrtaj liniju
        self.ax.plot(self.xs[-2:], self.ys[-2:], 'b-')
        print((timer()-starttime)*1000)

    def sensRangeUpdate(self):
        self.ax.set_ylim(0, int(self.sensRangeVar.get()) + 5)

    def animationStart(self):
        print("Anim. start called")
        if(self.validateInput()==True):
            print("Input validated")
        plt.axhline(y=float(self.entryPritisakOtvaranja.get()), color="RED")
        self.paramBoxBuff = []
        self.ani = animation.FuncAnimation(self.fig, self.animate, fargs=(self.xs, self.ys), interval=50)
        self.canvas.draw()

    def animationStop(self):

        ani = self.ani.event_source.stop()
        data = [self.entrySerBrojVentila.get(), self.entryLokacijaVentila.get(), self.entryRadniMedijVentila.get(), self.entryPritisakOtvaranja.get(), self.radniMedijVar.get()]

        report = ReportMaker.makeReport(self, data)



    def validateInput(self):
        print("ValidateInput called!")
        valid = True
        if not(self.entrySerBrojVentila.get()):
            valid = False
            print("ser broj nije ok")
        if not(float(self.entryPritisakOtvaranja.get())):
            valid = False
            print("pritisak otvaranjaok")
        else:
            if(float(self.entryPritisakOtvaranja.get())>float(self.sensRangeVar.get())):
                print("Pritisak otvaranja veci od senzora")
                valid = False
        return valid

class serialCom():

    def __init__(self):
        self.ser = ""

    def open(self, button, port):
        self.ser = serial.Serial(port, 9600, timeout=0.1, )
        time.sleep(2)
        if(self.ser.inWaiting()>0):
            button.config(fg="GREEN")
            return True
        return False

    def getPorts(self):
        portsAvailable = serial.tools.list_ports.comports()
        return portsAvailable


    def isOpen(self):
        if (self.ser.inWaiting() > 0):
            return True
        return False

    def getData(self):

        if (self.ser.inWaiting() > 0):

            starttime = timer()
            data = self.ser.read(self.ser.inWaiting()).decode()
            if '\r\n' in data:
                data = data.split('\r\n')
            return data[-2]
        return False

class StatusBar(tk.Frame):
   def __init__(self, master):
      tk.Frame.__init__(self, master)
      self.label = tk.Label(self, bd = 1, relief = "sunken", anchor = "w")
      self.label.pack(fill="x")
   def set(self, format0, *args):
      self.label.config(text = format0 % args)
      self.label.update_idletasks()
   def clear(self):
      self.label.config(text="")
      self.label.update_idletasks()

class MenuClass(tk.Frame):
   def __init__(self, parent):
       self.parent = parent
       menuBar = tk.Menu(self.parent)
       self.parent.config(menu=menuBar)

       file_menu = tk.Menu(menuBar, tearoff=0)

       menuBar.add_cascade(label="Glavni meni", menu=file_menu)
       file_menu.add_separator()
       file_menu.add_command(label='Izlaz', command=self.parent.quit)

class ReportMaker(tk.Frame):
    def __init__(self, parent):
        self.parent = parent

    def makeReport(self, data):
        self.data  = data
        newReport = open("reports/" + str(time.time()) + "_" + str(data[0]), "w")
        with open("templates/reportTemplate.html", "r+") as reportTemplate:
            content = reportTemplate.read()
            content = content.replace("{serbroj}", str(data[0]))
            print(content)
            newReport.write(content)

        reportTemplate.close()
        newReport.close()
        return True




root = tk.Tk()
root.geometry("800x800")
app = pyValveApp(root)
root.mainloop()

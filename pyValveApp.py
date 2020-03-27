import tkinter as tk
import time
import serial
import serial.tools.list_ports
import matplotlib as plt


class pyValveApp(tk.Frame):
    def __init__(self, parent):
        self.parent = parent

        fontBold = "helvetica 14 bold"
        fontRegular = "helvetica 13"

        parent.title("pyValve v0.2")
        self.frame = tk.Frame(self.parent)
        labelPodaci = tk.Label(self.parent, text="Osnovni podaci o ventilu",font=fontBold)
        labelPodaci.place(x=20, y=10)

        #Lokacija ventila
        labelLokacijaVentila = tk.Label(self.parent, text="Lokacija ventila:", bd=1, font=fontRegular)
        labelLokacijaVentila.place(x=30, y=55)
        entryLokacijaVentila = tk.Entry(self.parent)
        entryLokacijaVentila.place(x=150, y=50)

        #Serijski broj
        labelSerBrojVentila = tk.Label(self.parent, text="Serijski broj:", bd=1, font=fontRegular)
        labelSerBrojVentila.place(x=30, y=85)
        entrySerBrojVentila = tk.Entry(self.parent)
        entrySerBrojVentila.place(x=150, y=80)

        #Nominalni precnik
        labelPrecnikVentila = tk.Label(self.parent, text="Nominalni prečnik:", font=fontRegular)
        labelPrecnikVentila.place(x=30, y=115)

        entryPrecnikVentila = tk.Entry(self.parent)
        entryPrecnikVentila.place(x=150, y=110)

        #Radni medijum
        labelRadniMedijVentila = tk.Label(self.parent, text="Radni medijum:", font=fontRegular)
        labelRadniMedijVentila.place(x=30, y=145)

        entryRadniMedijVentila = tk.Entry(self.parent)
        entryRadniMedijVentila.place(x=150, y=140)

        labelIspitniPodaci = tk.Label(self.parent, text="Ispitni podaci", font=fontBold)
        labelIspitniPodaci.place(x=30, y=180)

        #Pritisak početka otvaranja

        labelPritisakOtvaranja = tk.Label(self.parent, text="Pritisak otvaranja:", font=fontRegular)
        labelPritisakOtvaranja.place(x=30, y=215)

        entryPritisakOtvaranja = tk.Entry(self.parent)
        entryPritisakOtvaranja.place(x=150, y=210)

        #Ispitni medijum
        labelRadniMedijVentila = tk.Label(self.parent, text="Ispitni medijum:", font=fontRegular)
        labelRadniMedijVentila.place(x=30, y=245)

        radniMedijVar = tk.StringVar(self.parent)
        radniMedijList = ["N2", "Voda"]
        radniMedijVar.set(radniMedijList[0])

        selRadniMedijVentila = tk.OptionMenu(self.parent, radniMedijVar, *radniMedijList)
        selRadniMedijVentila.place(x=150, y=240)

        #Port selection

        #label
        labelPortSel = tk.Label(self.parent, text="Interfejs senzora", font=fontBold)
        labelPortSel.place(x=420, y=10)

        #Serijski port
        labelSerPort = tk.Label(self.parent, text="Izaberi port", font=fontRegular)
        labelSerPort.place(x=420, y=40)

        self.serPortVar = tk.StringVar(self.parent)
        self.serPortList = [port.device for port in serialCom.getPorts()]

        if(self.serPortList):
            self.serPortVar.set(self.serPortList[0])
        self.selSerPort = tk.OptionMenu(self.parent, self.serPortVar, *self.serPortList)
        self.selSerPort.place(x=420, y=70)

        self.buttonOpenSerial = tk.Button(text="Konektuj interfejs", command=lambda: serialCom.open(self, self.parent, self.serPortVar.get()))
        self.buttonOpenSerial.place(x=470, y=100)

        self.buttonCheck = tk.Button(text="Provjeri interfejs", command=lambda: serialCom.isOpen(self, self.parent, self.serPortVar.get()))
        self.buttonCheck.place(x=470, y=130)

        self.frame.pack()

class serialCom():

    ser = ""

    def open(self, parent, port):
        self.ser = serial.Serial(port, 9600, timeout=0.1, )
        time.sleep(2)
        if(self.ser.inWaiting()>0):
            print(self.ser.readline().decode())
            self.buttonOpenSerial.config(fg="GREEN")
            return True
        return False

    def getPorts():
        portsAvailable = serial.tools.list_ports.comports()
        return portsAvailable

    def isOpen(self, parent, port):
        if (self.ser.inWaiting() > 0):
            self.ser.reset_input_buffer()
            print(self.ser.readline().decode())
            self.ser.reset_input_buffer()
            return True
        return False


root = tk.Tk()
root.geometry("800x600")

app = pyValveApp(root)
root.mainloop()

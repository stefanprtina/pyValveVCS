import tkinter as tk
from tkinter import ttk
import time
from timeit import default_timer as timer
import serial
import serial.tools.list_ports
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.offsetbox import AnchoredText
import numpy as np
from baza.dbModel import dbModel

class pyValveApp(tk.Frame):
    def __init__(self, parent):
        self.parent = parent

        dbConn = dbModel(self.parent)
        self.dbConn = dbConn.connect()

        # Status bar
        self.statusBar = StatusBar(self.parent)
        self.statusBar.pack(side="bottom", fill="x")

        self.glavniMeni = MenuClass(self.parent)
        self.ani = " "


        self.serialInst = serialCom()

        fontBold = "helvetica 14 bold"
        fontRegular = "helvetica 13"

        parent.title("pyValve v0.2")
        self.frameMain = tk.Frame(self.parent, width=1000, height=800, background="")

        self.frameMain.tkraise()
        self.frameMain.labelPodaci = tk.Label(self.frameMain, text="Osnovni podaci o ventilu",font=fontBold)
        self.frameMain.labelPodaci.place(x=20, y=10)

        #Lokacija ventila
        self.frameMain.labelLokacijaVentila = tk.Label(self.frameMain, text="Lokacija ventila:", bd=1, font=fontRegular)
        self.frameMain.labelLokacijaVentila.place(x=30, y=55)

        self.frameMain.entryLokacijaVentila = tk.Entry(self.frameMain)
        self.frameMain.entryLokacijaVentila.place(x=150, y=50)

        #Serijski broj
        self.frameMain.labelSerBrojVentila = tk.Label(self.frameMain, text="Serijski broj:", bd=1, font=fontRegular)
        self.frameMain.labelSerBrojVentila.place(x=30, y=85)
        self.frameMain.entrySerBrojVentila = tk.Entry(self.frameMain)
        self.frameMain.entrySerBrojVentila.place(x=150, y=80)

        #Nominalni precnik
        self.frameMain.labelPrecnikVentila = tk.Label(self.frameMain, text="Nominalni prečnik:", font=fontRegular)
        self.frameMain.labelPrecnikVentila.place(x=30, y=115)

        self.frameMain.entryPrecnikVentila = tk.Entry(self.frameMain)
        self.frameMain.entryPrecnikVentila.place(x=150, y=110)

        #Radni medijum
        self.frameMain.labelRadniMedijVentila = tk.Label(self.frameMain, text="Radni medijum:", font=fontRegular)
        self.frameMain.labelRadniMedijVentila.place(x=30, y=145)

        self.frameMain.entryRadniMedijVentila = tk.Entry(self.frameMain)
        self.frameMain.entryRadniMedijVentila.place(x=150, y=140)

        self.frameMain.labelIspitniPodaci = tk.Label(self.frameMain, text="Ispitni podaci", font=fontBold)
        self.frameMain.labelIspitniPodaci.place(x=30, y=180)

        #Pritisak početka otvaranja

        self.frameMain.labelPritisakOtvaranja = tk.Label(self.frameMain, text="Pritisak otvaranja:", font=fontRegular)
        self.frameMain.labelPritisakOtvaranja.place(x=30, y=215)

        self.frameMain.entryPritisakOtvaranja = tk.Entry(self.frameMain)
        self.frameMain.entryPritisakOtvaranja.place(x=150, y=210)

        #Ispitni medijum
        self.frameMain.labelRadniMedijVentila = tk.Label(self.frameMain, text="Ispitni medijum:", font=fontRegular)
        self.frameMain.labelRadniMedijVentila.place(x=30, y=245)

        self.radniMedijVar = tk.StringVar(self.parent)
        self.radniMedijList = ["N2", "Voda"]
        self.radniMedijVar.set(self.radniMedijList[0])

        self.selRadniMedijVentila = tk.OptionMenu(self.frameMain, self.radniMedijVar, *self.radniMedijList)
        self.selRadniMedijVentila.place(x=150, y=240)

        #Port selection

        #label
        self.frameMain.labelPortSel = tk.Label(self.frameMain, text="Interfejs senzora", font=fontBold)
        self.frameMain.labelPortSel.place(x=420, y=10)

        #Serijski port
        self.frameMain.labelSerPort = tk.Label(self.frameMain, text="Izaberi port", font=fontRegular)
        self.frameMain.labelSerPort.place(x=420, y=40)

        self.serPortVar = tk.StringVar(self.parent)
        self.frameMain.serPortList = [port.device for port in self.serialInst.getPorts()]

        if(self.frameMain.serPortList):
            self.serPortVar.set(self.frameMain.serPortList[0])
        self.frameMain.selSerPort = tk.OptionMenu(self.frameMain, self.serPortVar, *self.frameMain.serPortList)
        self.frameMain.selSerPort.place(x=420, y=70)

        self.frameMain.buttonOpenSerial = tk.Button(self.frameMain, text="Konektuj interfejs", command=lambda: self.serialInst.open(self.frameMain.buttonOpenSerial, self.serPortVar.get()))
        self.frameMain.buttonOpenSerial.place(x=470, y=100)


        self.frameMain.labelSerPort = tk.Label(self.frameMain, text="Izaberi mjerno područje transmitera(bar)", font=fontRegular)
        self.frameMain.labelSerPort.place(x=420, y=160)
        self.sensRangeVar = tk.StringVar(self.parent)
        self.sensRangeList = [10, 25, 100, 200, 300, 500]
        self.sensRangeVar.set(self.sensRangeList[0])
        sensRangeMenu = tk.OptionMenu(self.frameMain, self.sensRangeVar, *self.sensRangeList)
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

        self.frameMain.canvas = FigureCanvasTkAgg(self.fig, master=self.frameMain)  # A tk.DrawingArea.
        self.frameMain.canvas.draw()
        self.toolbar = NavigationToolbar2Tk(self.frameMain.canvas, self.parent)
        self.toolbar.update()
        self.frameMain.canvas.get_tk_widget().place(x=20, y=280)

        self.frameMain.buttonPocetak = tk.Button(self.frameMain, text="Počni ispitivanje", command=self.animationStart)
        self.frameMain.buttonPocetak.place(x=470, y=240)

        self.frameMain.buttonKraj = tk.Button(self.frameMain, text="Završi ispitivanje", command=self.animationStop)
        self.frameMain.buttonKraj.place(x=470, y=270)

        self.frameMain.buttonBaza = tk.Button(self.frameMain, text="Baza podataka", command=lambda: dbManager.open(self, self.parent))
        self.frameMain.buttonBaza.place(x=600, y=20)

        self.frameMain.pack()
        #self.frameMain.pack_forget()

        self.frameDB = tk.Frame(self.parent, width=1000, height=800)




    def animate(self, i, xs, ys):

        starttime = timer()
        xs = self.xs
        ys = self.ys

        if(ys):
            ymax = max(self.ys)

        mappedVal = np.interp(self.serialInst.getData(), [0.0, 1023.0], [0.0, float(self.sensRangeVar.get())])
        if(self.xs):
            self.xs.append(xs[-1]+0.05)
            if(max(self.xs) > max(self.ax.get_xlim())):
              self.ax.set_xlim(0, (max(self.ax.get_xlim())+2))

        else:
            self.xs = [0.05]

        self.ys.append(mappedVal)

        # Limit x and y lists to 20 items
        self.xs = self.xs[-200:]
        self.ys = self.ys[-200:]


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
            plt.axhline(y=float(self.frameMain.entryPritisakOtvaranja.get()), color="RED")
            self.paramBoxBuff = []
            self.ani = animation.FuncAnimation(self.fig, self.animate, fargs=(self.xs, self.ys), interval=50)
            self.frameMain.canvas.draw()
            return False

    def animationStop(self):

        ani = self.ani.event_source.stop()
        data = [self.frameMain.entrySerBrojVentila.get(), self.frameMain.entryLokacijaVentila.get(), self.frameMain.entryPrecnikVentila.get(), self.frameMain.entryRadniMedijVentila.get(), self.frameMain.entryPritisakOtvaranja.get(), self.radniMedijVar.get()]
        imgName = "dijagrami/" + str(self.frameMain.entrySerBrojVentila.get()) + "__"+str(time.time()) + ".png"
        print(imgName)
        try:
            plt.savefig(imgName, dpi=200, bbox_inches="tight")
            data.append(imgName)
            print(data)
            print("Dijagram sacuvan")
        except:
            print("ERROR - slika nije sacuvana")

        report = ReportMaker.makeReport(self, data)



    def validateInput(self):
        print("ValidateInput called!")
        valid = True
        if not(self.frameMain.entrySerBrojVentila.get()):
            valid = False
            self.frameMain.entrySerBrojVentila.config(bg="#ffbda1")
            tk.messagebox.showerror("Nije unijet serijski broj ventila")
            print("ser broj nije ok")
        if not(float(self.frameMain.entryPritisakOtvaranja.get())):
            valid = False
            self.frameMain.entryPritisakOtvaranja.config(bg="#ffbda1")
            tk.messagebox.showerror("Nije unijet pritisak otvaranja ventila")
            print("pritisak otvaranja ok")
        else:
            if(float(self.frameMain.entryPritisakOtvaranja.get())>float(self.sensRangeVar.get())):
                tk.messagebox.showerror("Greška unosa", "Pritisak otvaranja veci od maksimalnog pritiska transmitera")
                self.entryPritisakOtvaranja.config(bg="#ffbda1")
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
            print(data)
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
        newReport = open("reports/" + str(time.time()) + "_" + str(data[0]) + ".html", "w")
        with open("templates/reportTemplate.html", "r+", encoding="utf8") as reportTemplate:
            content = reportTemplate.read()
            content = content.replace("{serbroj}", str(data[0]))
            content = content.replace("{lokacija}", str(data[1]))
            content = content.replace("{precnik}", str(data[2]))
            content = content.replace("{medijum}", str(data[3]))
            content = content.replace("{pritisak}", str(data[4]))
            content = content.replace("{ispMedij}", str(data[5]))
            content = content.replace("{slika}", str(data[6]))

            newReport.write(content)

        reportTemplate.close()
        newReport.close()
        return True

class dbManager(tk.Frame):
    def __init__(self, parent):
        self.parent = parent

    def open(self, parent):
        self.parent = parent

        label = tk.Label(self.frameDB, text="Baza podataka firmi i ventila", font="helvetica 14 bold")
        label.place(x=300, y=5)
        self.frameDB.treeFirme = ttk.Treeview(self.frameDB)
        self.frameDB.treeFirme["columns"] = ("naziv")
        self.frameDB.treeFirme.column("#0", width=500, minwidth=270, stretch=tk.NO)

        self.frameDB.treeFirme.heading("#0", text="Naziv firme", anchor=tk.W)
        self.frameDB.treeFirme.place(x=30, y=40)

        self.frameDB.labelFrame = tk.LabelFrame(self.frameDB, text="Unos firme", font="helvetica 14 bold")
        self.frameDB.labelFrame.grid(row=3, column=2, padx=5, pady=5)
        self.frameDB.labelFrame.place(x=30, y=260)

        label= tk.Label(self.frameDB.labelFrame, text="Naziv:", font="helvetica 12")
        label.grid(row=0, column=0)
        self.frameDB.entryNazivFirme  = tk.Entry(self.frameDB.labelFrame)
        self.frameDB.entryNazivFirme.grid(column=1, row=0)

        label= tk.Label(self.frameDB.labelFrame, text="Podaci firme:", font="helvetica 12")
        label.grid(row=1, column=0)
        self.frameDB.entryPodaciFirme = tk.Text(self.frameDB.labelFrame, height=5, width=40, borderwidth=1, relief="solid")
        self.frameDB.entryPodaciFirme.grid(column=1, row=1)

        self.frameDB.buttonDodajFirmu = tk.Button(self.frameDB.labelFrame, text="Unesi firmu", command=lambda: dbManager.dodajfirmu(self))
        self.frameDB.buttonDodajFirmu.grid(column=1, row=2, sticky="se")


#podaci - baza

        query = self.dbConn.cursor()

        query.execute("SELECT rowid, naziv, podaci FROM firme ORDER BY rowid ASC")

        self.dbConn.commit()
        firme = query.fetchall()
        for firma in firme:
            print (firma[0])
            #nadji ventile u firmi
            sql = 'SELECT * FROM ventili WHERE firma =' + str(firma[0])
            query.execute(sql)
            ventili = query.fetchall()
            #-------------------------------------
            firmaTree = self.frameDB.treeFirme.insert("", "1", text=str(firma[1]), values=(str(firma[0])))
            for ventil in ventili:
                self.frameDB.treeFirme.insert(firmaTree, "end", text=(str(ventil[1]) + "//" + str(ventil[2])))

        self.frameMain.pack_forget()
        self.frameDB.pack()

    def dodajfirmu(self):
        firmaNaziv = self.frameDB.entryNazivFirme.get()
        firmaPodaci = self.frameDB.entryPodaciFirme.get("1.0", "end")
        sql = "INSERT INTO firme (naziv, podaci) VALUES('"+ firmaNaziv +"', '" + firmaPodaci+ "')"
        print(sql)
        dodato = self.dbConn.execute(sql)
        self.dbConn.commit()
        if(dodato):
            self.frameDB.treeFirme.insert("", "1", text=firmaNaziv)
            return True









root = tk.Tk()
root.geometry("800x800")
app = pyValveApp(root)
root.mainloop()

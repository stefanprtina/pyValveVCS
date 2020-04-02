import tkinter as tk
import time
import serial
import serial.tools.list_ports
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)

ani=""

class pyValveApp(tk.Frame):

    def __init__(self, parent):
        global ani
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(1, 1, 1)
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(0, 2.2)
        self.ani = " "
        self.parent = parent
        self.frame = tk.Frame(self.parent)
        self.buttonDijagram = tk.Button(text="Počni ispitivanje", command=self.animationStart)
        self.buttonDijagram.pack()
        ani = self.animationStart()

    def animationStart(self):
        print("Anim. start called")
        global ani
        ani = animation.FuncAnimation(self.fig, self._animate, interval=50)
        plt.show()

    def _animate(self, i):
        self.xs = []
        self.ys = []
        print("Animate called")




root = tk.Tk()
root.geometry("800x800")
app = pyValveApp(root)
root.mainloop()


class reportMaker(tk.Frame):

    def __init__(self, parent):
        self.parent = parent

    def makeReport(self, data):
        self.data = data

        width, height = A4

        tdata = [["Tablica podataka ventila koji je ispitan"],
            ["Serijski broj:", self.data[0]],
            ["Tip", "ventil sa oprugom"],
            ["Lokacija", self.data[1]],
            ["Radni medij", self.data[2]],
            ["Pritisak podešavanja", self.data[3]]]

        tabela = rTable(tdata, colWidths=[8 * cm, 8 * cm])
        tabela.setStyle(rTableStyle([
            ("SPAN", (0,0), (1,0)),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ]))
        story = []
        story.append(tabela)
        pdf = io.BytesIO()
        doc = SimpleDocTemplate(pdf, pagesize=A4)
        print(story)
        doc.build(story)
        pdf.seek(0)
        return pdf


        pdf = FPDF()
        # compression is not yet supported in py3k version
        pdf.compress = False
        pdf.add_page()
        # Unicode is not yet supported in the py3k version; use windows-1252 standard font
        pdf.set_font('Arial', 'B', 18)
        pdf.image("header.png", 0, 0, 200)
        pdf.ln(35)
        pdf.write(5, "IZVJESTAJ O ISPITIVANJU SIGURNOSNOG VENTILA")
        pdf.set_font('Arial', '', 14)
        pdf.ln(15)
        text = "Serijski broj ventila: " + str(data[0])
        pdf.write(5, text)
        pdf.ln(5)
        text = "Lokacija ventila: " + str(data[1])
        pdf.write(5, text)
        pdf.ln(5)
        text = "Radni medij: " + str(data[2])
        pdf.write(5, text)

        pdf.ln(10)
        text = "Pritisak otvaranja: " + str(data[3]) + " bar"
        pdf.write(5, text)
        pdf.ln(15)

        pdf.set_font('Arial', 'B', 16)
        pdf.write(5, "Podaci o ispitivanju ventila")
        pdf.ln(10)

        pdf.set_font('Arial', '', 14)
        text = "Ispitni medijum: " + str(data[4]) + " bar"
        pdf.write(5, text)


        pdf.output('py3k.pdf', 'F')
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

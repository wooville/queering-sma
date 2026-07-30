from . import multiprocessing
from . import math
from . import sounddevice as sd
from . import numpy as np
from . import signal
from . import pyglet
from . import imgui, immapp
from .helpers import *
from .simulation import QSMASimulation
from .window import QSMAWindow

# QSMACore creates an instance of QSMASimulation (sim) and QSMAWindow (win)
# when it creates QSMAWindow, it passes t
class QSMACore():
    # constants
    # window dimensions
    WIDTH = int(800)
    HEIGHT = int(800)
    FRAME_RATE = 60.0           # how many times/second does the program update (ie simulation speed); tihs is a maximum value limited by performance

    # when you open the program, it will read from PARAMS_FILE_READ 
    # if you press the SAVE PARAMETERS button, it will save to PARAMS_FILE_WRITE
    PARAMS_FILE_READ = "params_default.json"
    PARAMS_FILE_WRITE = "params_override.json"

    def __init__(self):
        # see params files for example structure
        self.core_params = read_json(self.PARAMS_FILE_READ)
        self.sim_params = self.core_params["sim_params"]

        # instantiate QSMASimulation logic
        self.sim = QSMASimulation()
        self.win = QSMAWindow(sim=self.sim, width=800, height=600, title="QSMA SIM", resizable=True)
        # set a framerate for the window
        pyglet.clock.schedule_interval(self.update, 1/self.FRAME_RATE)
    
    def update(self, dt):
        self.sim.update(dt)

    # called by main.py
    def run(self):
        # run pyglet window
        pyglet.app.run()
    
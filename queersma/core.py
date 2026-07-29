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

class QSMACore():
    # constants
    # window dimensions
    WIDTH = int(800)
    HEIGHT = int(800)

    FRAME_RATE = 60.0           # how many times/second does the program update (ie simulation speed); tihs is a maximum value limited by performance
    AGENT_SCALE_FACTOR = 1.0    # scale of drawn agent sprites (does not affect logic)

    # parameters start with default values from PARAMS_FILE_READ
    # if you press the Export Parameters button, 
    PARAMS_FILE_READ = "params_default.json"
    PARAMS_FILE_WRITE = "params_override.json"

    def __init__(self):
        # create signals using Blinker library
        # use signals to communicate between QSMA modules
        self.signals = {
            'sim_params_changed': signal('sim_params_changed')
            }

        # batches
        self.batch_trail = pyglet.graphics.Batch()
        self.batch_agents = pyglet.graphics.Batch()
        self.batches = np.asarray([self.batch_trail, self.batch_agents])

        # see params file for example structure
        self.core_params = read_json(self.PARAMS_FILE_READ)
        self.sim_params = self.core_params["sim_params"]

        # instantiate QSMASimulation logic
        self.sim = QSMASimulation(params=self.sim_params, signals=self.signals, batches=self.batches)
        # self.sim.restart()

        # if (self.run_QSMAWindow):
        # instantiate QSMAWindow to render QSMASimulation
        
        
        self.window = QSMAWindow(data={"sim": self.sim, "batches": self.batches, 'signals':self.signals}, width=800, height=600, title="QSMA SIM", resizable=True)
        # set a framerate for the window
        pyglet.clock.schedule_interval(self.update, 1/self.FRAME_RATE)

        # if (self.run_imgui)
        

    def update(self, dt):
        self.sim.update(dt)

    def run(self):
        # with multiprocessing.Pool() as pool:
        # run pyglet window
        pyglet.app.run()
        # run separate imgui window out of the box
        # gui_params = immapp.RunnerParams()
        # gui_params.app_window_params.window_title = "QSMA GUI"
        # immapp.run_async(gui_function=self.draw_gui)

    # def restart_sim():
    #     pass

    
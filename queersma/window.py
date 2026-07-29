from . import signal
from . import pyglet
from . import numpy as np
from . import math
from . import random
from . import imgui, create_renderer
from .helpers import write_json
from pyglet.window import key
from pyglet.gl import *
from pyglet.math import Mat4, Vec3

from typing import override

class QSMAWindow(pyglet.window.Window):
    def __init__(self, data, width, height, title, resizable):
        super().__init__(width, height, title, resizable)
        # pyglet.gl.glClearColor(random.random(), random.random(), random.random(), 1.0)
        self.sim = data['sim']
        self.signal_sim_params_changed = data['signals']['sim_params_changed']
        
        # self.batch_trail = data['batches'][0]
        # self.batch_agents = data['batches'][1]
        self.width = self.sim.params["width"]
        self.height = self.sim.params["height"]
        self.batch_trail = pyglet.graphics.Batch()
        self.batch_agents = pyglet.graphics.Batch()
        self.RGB_CHANNELS = 4
        self.MAX_COLOR = 255
        self.IMG_FORMAT = 'RGBA'
        self.pitch = self.width * self.RGB_CHANNELS

        # image_data draws to the screen
        self.image_data = pyglet.image.ImageData(
            self.width, self.height, self.IMG_FORMAT, self.sim.environment_map.tobytes(), self.pitch
        )
        
        # sprite is the visualization of the trail map
        self.sprite = pyglet.sprite.Sprite(self.image_data, batch=self.batch_trail)
        self.sprite = pyglet.shapes.Rectangle(x=self.sim.agents[0].x, y=self.sim.agents[0].y, width=4, height=4, color=self.sim.agents[0].color, batch=self.batch_agents)
        
        # self.environment_map = np.zeros(
        #     [self.height, self.width, self.RGB_CHANNELS], dtype=np.uint8 # note that height/width are swapped, don't worry too much about it...
        #     )
        
        # self.agent_sprites = np.empty(self.sim.params["agents_number"])
        # for i in range(self.sim.agents.size):
        #     a = self.sim.agents[i]
        #     print(a.x)
        #     self.agent_sprites[i]=pyglet.shapes.Rectangle(x=a.x, y=a.y, width=1, height=1, color=a.color, batch=self.batch_agents)

        self.show_trail = True
        self.show_agents = True
        self.show_fps = True

        # Setup visual elements
        self.fps_display = pyglet.window.FPSDisplay(window=self)
        imgui.create_context()
        self.renderer = create_renderer(self)
        

    # the window executes this function when we press any key
    @override
    def on_key_press(self, symbol, modifiers):
        # if symbol == key.R:
        #     print('Restarting simulation!')
        #     restart_sim()
        if symbol == key.F:
            print('FPS display toggled')
            self.show_fps = not self.show_fps
            
        # elif symbol == key.ENTER:
        #     print('The enter key was pressed.')
    
    @override
    def on_draw(self):
        # erase the previous frame drawing
        self.clear()
        
        # the simulation canvas is a sim.width x sim.height area; scale it to fill
        # the window (preserving aspect ratio) and center whatever's left over
        # scale = min(self.width / self.sim.width, self.height / self.sim.height)
        # offset_x = (self.width - self.sim.width * scale) / 2
        # offset_y = (self.height - self.sim.height * scale) / 2
        # self.view = Mat4.from_translation(Vec3(offset_x, offset_y, 0)) @ Mat4.from_scale(Vec3(scale, scale, 1))

        # draw the trail map sprite before (underneath) the agent sprites
        # if self.show_trail: self.batch_trail.draw()
        # if self.show_agents: self.batch_agents.draw()
        self.image_data.set_data(self.IMG_FORMAT, self.pitch, self.sim.environment_map.tobytes()) # turn the colors into bytes and store it as an image
        # print(self.sim.environment_map.tobytes())
        self.sprite.image = self.image_data

        self.batch_trail.draw()
        self.batch_agents.draw()

        # reset the view so the fps display and gui aren't shifted by the offset
        # self.view = Mat4()
        if self.show_fps: self.fps_display.draw()

        self.draw_gui()

    # draw a simple "immediate mode" gui using imgui-bundle library
    # define interface elements (text, checkboxes, sliders) to be drawn every frame
    # the drawn interface elements are interactable and can manipulate the parameters of the simulation
    def draw_gui(self):
        # global sim_params["agents_number"], sim_params["step_size"], sim_params["max_time_scale_factor"], sim_params["sensor_offset"], sim_params["sensor_angle"], sim_params["turn_angle"], sim_params["trail_decay"], sim_params["wander_chance"], sim_params["wander_weight"], sim_params["drift_chance"], sim_params["drift_weight"], 

        # begin gui definition
        # everything between imgui.begin() and imgui.end() defines the gui like an ordered list of elements
        imgui.new_frame()
        imgui.begin("Parameter Palette")
        # for param in self.core_params

        # checkboxes to toggle drawing of trail/agents
        # _, show_trail = imgui.checkbox("Show Trail", show_trail)
        # imgui.same_line()
        # _, show_agents = imgui.checkbox("Show Agents", show_agents)

        # sliders to adjust simulation parameters
        changed, self.sim.params["agents_number"] = imgui.slider_int(
            "AGENTS_NUMBER", self.sim.params["agents_number"], v_min=0, v_max=10000
        )
        changed, self.sim.params["step_size"] = imgui.slider_int(
            "STEP_SIZE", self.sim.params["step_size"], v_min=0, v_max=100
        )
        changed, self.sim.params["max_time_scale_factor"] = imgui.slider_float(
            "MAX_TIME_SCALE_FACTOR", self.sim.params["max_time_scale_factor"], v_min=0.5, v_max=10
        )
        changed, self.sim.params["sensor_offset"] = imgui.slider_int(
            "SENSOR_OFFSET", self.sim.params["sensor_offset"], v_min=-300, v_max=300
        )
        changed, self.sim.params["sensor_angle"] = imgui.slider_float(
            "SENSOR_ANGLE", self.sim.params["sensor_angle"], v_min=-math.pi, v_max=math.pi
        )
        changed, self.sim.params["turn_angle"] = imgui.slider_float(
            "TURN_ANGLE", self.sim.params["turn_angle"], v_min=-math.pi, v_max=math.pi
        )
        changed, self.sim.params["trail_decay"] = imgui.slider_float(
            "TRAIL_DECAY", self.sim.params["trail_decay"], v_min=-1, v_max=1
        )
        changed, self.sim.params["wander_chance"] = imgui.slider_float(
            "WANDER_CHANCE", self.sim.params["wander_chance"], v_min=0, v_max=1
        )
        changed, self.sim.params["wander_weight"] = imgui.slider_float(
            "WANDER_WEIGHT", self.sim.params["wander_weight"], v_min=0, v_max=1
        )
        changed, self.sim.params["drift_chance"] = imgui.slider_float(
            "DRIFT_CHANCE", self.sim.params["drift_chance"], v_min=0, v_max=1
        )
        changed, self.sim.params["drift_weight"] = imgui.slider_float(
            "DRIFT_WEIGHT", self.sim.params["drift_weight"], v_min=-1, v_max=1
        )

        # if anything changed, send signal to whoever is subscribed to 'sim_params_changed' signal
        if (changed):
            # print("test")
            self.signal_sim_params_changed.send(self)

        # if imgui.button("SAVE PARAMS"):
        #     write_json(self.core_params, self.PARAMS_FILE_WRITE)
        #     print("Parameters saved into ", self.PARAMS_FILE_WRITE)

        # end gui definition
        imgui.end()

        

        # draw the gui for this frame based on above definition
        imgui.render()
        self.renderer.render(imgui.get_draw_data())


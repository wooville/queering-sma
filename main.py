import os
import platform
import json

current_os = platform.system()
if (current_os == "Linux"): os.environ.setdefault("PYOPENGL_PLATFORM", "x11")

import math
import random
import numpy as np

import pyglet
if current_os == "Windows":
    pyglet.options.dpi_scaling = "real"
elif current_os == "Darwin":
    pyglet.options.dpi_scaling = "scaled"
elif current_os == "Linux":
    pyglet.options.dpi_scaling = "real"

from pyglet.window import key
from pyglet.gl import *
from pyglet.math import Mat4, Vec3
from imgui_bundle import imgui
from imgui_bundle.python_backends.pyglet_backend import create_renderer

# constants
# window dimensions
WIDTH = int(800)
HEIGHT = int(800)

FRAME_RATE = 60.0           # how many times/second does the program update (ie simulation speed); tihs is a maximum value limited by performance
AGENT_SCALE_FACTOR = 1.0    # scale of drawn agent sprites (does not affect logic)

# parameters start with default values from PARAMS_FILE_READ
# if you press the Export Parameters button, 
PARAMS_FILE_READ = "params_override.json"
PARAMS_FILE_WRITE = "params_override.json"

# object (dict) to store parameters into
# parameters are read 
# parameters are adjustable in the GUI
params = {}

# other gui/state tracking vars
show_trail = True
show_agents = True
show_fps = False
# counter = 0

# READ FROM FILE
with open(PARAMS_FILE_READ, "r") as f:
    params = json.load(f)
    sim_params = params["sim_params"]

# for reproducibility (haven't tested much)
# random.seed(0)
# np.random.seed(0)

# create the window containing the program
window = pyglet.window.Window(WIDTH, HEIGHT, resizable=True)
fps_display = pyglet.window.FPSDisplay(window=window)

# for efficient rendering of many sprites at once, we assign them to one of these batches
batch_trail = pyglet.graphics.Batch()
batch_agents = pyglet.graphics.Batch()

# define the format of the image that we draw the trail with
# RGBA format: Red Green Blue Alpha -> Alpha = opacity
RGB_CHANNELS = 4
MAX_COLOR = 255
IMG_FORMAT = 'RGBA'
pitch = WIDTH * RGB_CHANNELS

# create an empty canvas that corresponds to the size of the window
# this is a 3D array; each pixel on the screen (2D) has 4 values associated with it that collectively describe the color/opacity of that pixel (RGBA)
# pixels/colors are just an example for visualization, you can also think of it as a 2D grid that agents deposit their trails onto
# if there's no trail at a location, it's 
trail_map = np.zeros(
    [HEIGHT, WIDTH, RGB_CHANNELS], dtype=np.uint8 # note that height/width are swapped, don't worry too much about it...
)

# Don't worry too much about Observer and SimulationTimer
# Here, we define the timer that our simulation runs on
# Our Agents and Environment "observe" the SimulationTimer so that they know when to update

# Abstract observer class
class Observer:
    def __init__(self, subject):
        subject.push_handlers(self)

# The subject
class SimulationTimer(pyglet.event.EventDispatcher):
    def tick(self):
        self.dispatch_event('on_update') # tell everyone to update

SimulationTimer.register_event_type('on_update')

# Here, we define the behaviour of each individual agent
# When we run the program, we will create many of these agents that act based on our code here
# Agents move and turn  based on information retrieved by sensing the trail_map around them 
class Agent(Observer):
    # every time we create an Agent, we first initialize it based on this function
    def __init__(self, subject):
        subject.push_handlers(self)
        
        # this code spawns agents exactly in the middle of the window
        # self.x = window.width / 2
        # self.y = window.height / 2
        # self.dir = math.pi
        
        # Here, we initialize this individual agent's important variables (current position and direction)
        # These self.variable values are accessible in our other functions after this point
        # this code spawns agents randomly near the center of the window
        self.x = random.randint(WIDTH // 2 - WIDTH // 16, WIDTH // 2 + WIDTH // 16)
        self.y = random.randint(HEIGHT // 2 - HEIGHT // 16, HEIGHT // 2 + HEIGHT // 16)
        self.dir = (random.random()*math.pi)    # current direction in radians

        # assign a random color to this agent
        # RGBA format: Red Green Blue Alpha -> alpha = opacity
        self.color = (random.randint(0,255), random.randint(0,255), random.randint(0,255), 255)

        # assign a sprite to this agent (so we can draw it) and give it our (x,y) position, color
        self.sprite = pyglet.shapes.Rectangle(x=self.x, y=self.y, width=AGENT_SCALE_FACTOR, height=AGENT_SCALE_FACTOR, color=self.color, batch=batch_agents)

        # we could consider agents with individual parameters, instead of using the same global parameters for all agents (tangential)
        # self.sensor_offset = sim_params["sensor_offset"]
        # self.sensor_angle = sim_params["sensor_angle"]
        # self.turn_angle = sim_params["turn_angle"]
        # ...

    # called every frame: update direction and position based on global parameter values
    def on_update(self):
        self.update_direction()
        self.update_position()
    
    # decide on a new direction based on sensor data
    def update_direction(self):
        # acquire sensor data at 3 points (offset from the agent, fanned from left to right) 
        left = self.sense(-sim_params["sensor_angle"]*math.pi)
        center = self.sense(0)
        right = self.sense(+sim_params["sensor_angle"]*math.pi)
        
        # decide on a direction based on sensor data
        # update direction towards max sensed value by amount=sim_params["turn_angle"]
        if (center > left and center > right):
            pass
        elif (center < left and center > right):
            if (np.random.rand() < 0.5): self.dir += sim_params["turn_angle"]*math.pi
        elif (left > right):
            self.dir += -sim_params["turn_angle"]*math.pi
        elif (right > left):
            self.dir += sim_params["turn_angle"]*math.pi

        # check if we want to apply drift (random angle modifier)
        if (np.random.rand() < sim_params["drift_chance"]):
            self.dir += random.uniform(-sim_params["drift_weight"]*math.pi, sim_params["drift_weight"]*math.pi)

    # return the value of the trail_map at a point relative to ourselves (the agent)
    def sense(self, dir_offset):
        # check if wandering (return random value)
        # maybe more like "blind" at this sensor point
        if (np.random.rand() < sim_params["wander_chance"]):
            return random.randint(-int(sim_params["wander_weight"]*255), int(sim_params["wander_weight"])*255)
        
        # dir_offset is the angle relative to our current direction
        angle = self.dir + dir_offset

        # get x and y coordinates of the point a certain angle and distance (sim_params["sensor_offset"]) away from us 
        # x and y components of the point relative to ourselves
        x = math.floor(self.x + sim_params["sensor_offset"] * math.cos(angle))
        y = math.floor(self.y + sim_params["sensor_offset"] * math.sin(angle))

        # wrap x and y coordinates to contain them inside of the window (we don't want to go out of bounds)
        x = (x + WIDTH) % WIDTH
        y = (y + HEIGHT) % HEIGHT
        
        # # return the trail at this location (specifically the opacity; we ignore the color)
        return trail_map[y, x, :][3] # [3] is the alpha channel (highest trail intensity)
    
    # move self one step and update agent sprite
    def update_position(self):
        # calculate x and y components of current direction
        dx = math.cos(self.dir)
        dy = math.sin(self.dir)

        # this loops takes sim_params["step_size"] steps in unit increments
        for i in range(sim_params["step_size"]):
            # update location by one pixel
            self.x += dx
            self.y += dy
            self.x = (self.x + WIDTH) % WIDTH
            self.y = (self.y + HEIGHT) % HEIGHT
            self.deposit() # deposit trail at each step

        # update agent sprite with new location
        self.sprite.x = self.x
        self.sprite.y = self.y
    
    # deposit trail at current location (represented with a color value for visualization)
    def deposit(self):
        # this code makes all trails green
        # trail_map[int(self.y)][int(self.x)][:]  = [0,255,0,255]
        
        # if (pride_mode):
        trail_map[int(self.y)][int(self.x)][:] = self.color
        # else: trail_map[int(self.y)][int(self.x)][:] = param_trail_map_color

# object class that updates the environment that agents interact with
# we will create a single Environment, and all it does is update the value of the trail_map
class Environment(Observer):
    def __init__(self, subject):
        global trail_map # use the global trail_map we made earlier
        subject.push_handlers(self)

        # image_data draws to the screen
        self.image_data = pyglet.image.ImageData(
            WIDTH, HEIGHT, IMG_FORMAT, trail_map.tobytes(), pitch
        )
        
        # sprite is the visualization of the trail map
        self.sprite = pyglet.sprite.Sprite(self.image_data, batch=batch_trail)
    
    # called every frame by SimulationTimer: decay trail and update associated pixels 
    def on_update(self):
        global trail_map # use the global trail_map we made earlier

        # decay trails, making sure that we're storing valid numbers into trail_map (our RGBA format)
        trail_map = np.uint8(trail_map*sim_params["trail_decay"])

        self.image_data.set_data(IMG_FORMAT, pitch, trail_map.tobytes()) # turn the colors into bytes and store it as an image
        self.sprite.image = self.image_data # this is the sprite drawn by the window every frame

agents = np.empty(sim_params["agents_number"], Agent)
env = None

# make a simulation timer and the update function (tick)
simulation_timer = SimulationTimer()
def update_loop(dt):
    simulation_timer.tick()

# reset the simulation state (but not the parameters)
def restart_sim():
    global trail_map, agents, env, simulation_timer, update_loop # make sure we use the same set of variables when we reset, otherwise we're making new ones!
    pyglet.app.exit()
    pyglet.clock.unschedule(update_loop)
    
    trail_map = np.zeros(
    [HEIGHT, WIDTH, RGB_CHANNELS], dtype=np.uint8 # note that height/width are swapped, don't worry too much about it...
    )

    # simulation_timer runs the main loop of the simulation
    # dt = delta time; amount of time elapsed between updates (1/frame_rate)
    # everything else in the simulation (Environment and Agents) updates when simulation_timer.tick() is called
    
    # create our agents according to parameters
    agents = np.empty(sim_params["agents_number"], Agent)
    for i in range(sim_params["agents_number"]):
        agents[i] = Agent(simulation_timer) # each agent observes the same simulation timer
    
    # create our environment and give it the simulation timer to observe
    env = Environment(simulation_timer)

    # set the update_loop (tick the simulation timer) we want to run and the interval (framerate)
    pyglet.clock.schedule_interval(update_loop, 1/(FRAME_RATE*sim_params["max_time_scale_factor"]))  # update at FRAME_RATE Hz (FRAME_RATE updates/second)
    pyglet.app.run()
    # print("wow")

### window functions for drawing each frame and input processing, can ignore
# create the objects we use for rendering the gui
imgui.create_context()
renderer = create_renderer(window)

# scale up the gui (text + widget padding/sizes) for readability on HiDPI displays
UI_SCALE = 1.25
imgui.get_style().font_scale_main = UI_SCALE
imgui.get_style().scale_all_sizes(UI_SCALE)

# the window executes this function when we press any key
@window.event
def on_key_press(symbol, modifiers):
    if symbol == key.R:
        print('Restarting simulation!')
        restart_sim()
    elif symbol == key.F:
        global show_fps
        print('FPS display toggled')
        show_fps = not show_fps
        
    # elif symbol == key.ENTER:
    #     print('The enter key was pressed.')
# the window uses this function to draw each frame
@window.event
def on_draw():
    # erase the previous frame drawing
    window.clear()

    # the simulation canvas is a fixed WIDTH x HEIGHT area; scale it to fill
    # the window (preserving aspect ratio) and center whatever's left over
    scale = min(window.width / WIDTH, window.height / HEIGHT)
    offset_x = (window.width - WIDTH * scale) / 2
    offset_y = (window.height - HEIGHT * scale) / 2
    window.view = Mat4.from_translation(Vec3(offset_x, offset_y, 0)) @ Mat4.from_scale(Vec3(scale, scale, 1))

    # draw the trail map sprite before (underneath) the agent sprites
    if show_trail: batch_trail.draw()
    if show_agents: batch_agents.draw()

    # reset the view so the fps display and gui aren't shifted by the offset
    window.view = Mat4()
    if show_fps: fps_display.draw()

    # draw the gui on top of everything
    draw_gui()

# draw a simple "immediate mode" gui using imgui-bundle library
# define interface elements (text, checkboxes, sliders) to be drawn every frame
# the drawn interface elements are interactable and can manipulate the parameters of the simulation
def draw_gui():
    global sim_params
    global show_agents, show_trail
    # global sim_params["agents_number"], sim_params["step_size"], sim_params["max_time_scale_factor"], sim_params["sensor_offset"], sim_params["sensor_angle"], sim_params["turn_angle"], sim_params["trail_decay"], sim_params["wander_chance"], sim_params["wander_weight"], sim_params["drift_chance"], sim_params["drift_weight"], 

    # begin gui definition
    # everything between imgui.begin() and imgui.end() defines the gui like an ordered list of elements
    imgui.new_frame()
    imgui.begin("Parameter Palette")

    # checkboxes to toggle drawing of trail/agents
    _, show_trail = imgui.checkbox("Show Trail", show_trail)
    imgui.same_line()
    _, show_agents = imgui.checkbox("Show Agents", show_agents)

    # sliders to adjust simulation parameters
    changed_agents_number, sim_params["agents_number"] = imgui.slider_int(
        "AGENTS_NUMBER", sim_params["agents_number"], v_min=0, v_max=10000
    )
    changed_step_size, sim_params["step_size"] = imgui.slider_int(
        "STEP_SIZE", sim_params["step_size"], v_min=0, v_max=100
    )
    changed_sensor_angle, sim_params["max_time_scale_factor"] = imgui.slider_float(
        "MAX_TIME_SCALE_FACTOR", sim_params["max_time_scale_factor"], v_min=0.5, v_max=10
    )
    changed_sensor_offset, sim_params["sensor_offset"] = imgui.slider_int(
        "SENSOR_OFFSET", sim_params["sensor_offset"], v_min=-300, v_max=300
    )
    changed_sensor_angle, sim_params["sensor_angle"] = imgui.slider_float(
        "SENSOR_ANGLE", sim_params["sensor_angle"], v_min=-math.pi, v_max=math.pi
    )
    changed_turn_angle, sim_params["turn_angle"] = imgui.slider_float(
        "TURN_ANGLE", sim_params["turn_angle"], v_min=-math.pi, v_max=math.pi
    )
    changed_trail_decay, sim_params["trail_decay"] = imgui.slider_float(
        "TRAIL_DECAY", sim_params["trail_decay"], v_min=-1, v_max=1
    )
    changed_wander_chance, sim_params["wander_chance"] = imgui.slider_float(
        "WANDER_CHANCE", sim_params["wander_chance"], v_min=0, v_max=1
    )
    changed_wander_weight, sim_params["wander_weight"] = imgui.slider_float(
        "WANDER_WEIGHT", sim_params["wander_weight"], v_min=0, v_max=1
    )
    changed_drift_chance, sim_params["drift_chance"] = imgui.slider_float(
        "DRIFT_CHANCE", sim_params["drift_chance"], v_min=0, v_max=1
    )
    changed_drift_weight, sim_params["drift_weight"] = imgui.slider_float(
        "DRIFT_WEIGHT", sim_params["drift_weight"], v_min=-1, v_max=1
    )

    if imgui.button("SAVE PARAMS"):
        write_json(params, PARAMS_FILE_WRITE)
        print("Parameters saved into ", PARAMS_FILE_WRITE)

    # end gui definition
    imgui.end()

    # draw the gui for this frame based on above definition
    imgui.render()
    renderer.render(imgui.get_draw_data())

# start the program!!
restart_sim()

### EXTRAS
# helper function to write json file
def write_json(data, path):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

# this code makes the background of the window a random color
# pyglet.gl.glClearColor(random.random(), random.random(), random.random(), 1.0)

# unused multimedia functions
# image = pyglet.resource.image('kitten.jpg')
# music = pyglet.resource.media('music.mp3')
# music.play()
# sound = pyglet.resource.media('shot.wav', streaming=False)
# sound.play()

import math
import random
import numpy as np
import pyglet
from pyglet.window import key
from pyglet.gl import *
from imgui_bundle import imgui
from imgui_bundle.python_backends.pyglet_backend import create_renderer

# disable texture filters to avoid blurring pixels (doesn't seem to be necessary)
glEnable(GL_TEXTURE_2D)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

# window dimensions
WIDTH = int(512*1.25)
HEIGHT = int(512*1.25)

# constants
FRAME_RATE = 60.0           # how many times/second does the program update (ie simulation speed); tihs is a maximum value limited by performance
AGENT_SCALE_FACTOR = 1.0    # scale of drawn agent sprites (does not affect logic)

# gui-adjustable parameters
param_time_step_factor = 1.0        #NOTE must restart to take effect
param_agents_number = 1000          #NOTE must restart to take effect
param_sensor_offset = 10            #
param_sensor_angle = math.pi / 4    #
param_turn_angle = math.pi / 9      #
param_step_size = 1                 #
param_max_time_scale_factor = 1     #
param_trail_decay = 0.95            #
param_wander_chance = 0.003         #
param_wander_weight = 124           #
param_drift_chance = 0.05           #
param_drift_weight = math.pi / 12   #
# other gui/state tracking vars
show_trail = True
show_agents = True
# counter = 0

# for reproducibility (haven't tested much)
# random.seed(0)
# np.random.seed(0)

# window containing the program
window = pyglet.window.Window(WIDTH, HEIGHT)

# for efficient rendering of many sprites at once 
batch_trail = pyglet.graphics.Batch()
batch_agents = pyglet.graphics.Batch()

# create 
RGB_CHANNELS = 4
MAX_COLOR = 255
IMG_FORMAT = 'RGBA'
pitch = WIDTH * RGB_CHANNELS

screen = np.zeros(
    [HEIGHT, WIDTH, RGB_CHANNELS], dtype=np.uint8
)
trail_map = np.zeros(
    [HEIGHT, WIDTH, RGB_CHANNELS], dtype=np.uint8
)

# pyglet.gl.glClearColor(random.random(), random.random(), random.random(), 1.0)

# unused multimedia functions

# image = pyglet.resource.image('kitten.jpg')
# music = pyglet.resource.media('music.mp3')
# music.play()
# sound = pyglet.resource.media('shot.wav', streaming=False)
# sound.play()

# Abstract observer class
class Observer:
    def __init__(self, subject):
        subject.push_handlers(self)

# The subject
class SimulationTimer(pyglet.event.EventDispatcher):
    def tick(self):
        self.dispatch_event('on_update')

SimulationTimer.register_event_type('on_update')

# an object class representing a single agent
# agents move and turn sense the trail_map 
class Agent(Observer):
    def __init__(self, subject):
        subject.push_handlers(self)
        
        # this code spawns agents exactly in the middle of the window
        # self.x = window.width / 2
        # self.y = window.height / 2
        # self.dir = math.pi
        
        # this code spawns agents randomly near the center of the window
        self.x = random.randint(window.width // 2 - window.width // 16, window.width // 2 + window.width // 16)
        self.y = random.randint(window.height // 2 - window.height // 16, window.height // 2 + window.height // 16)
        self.dir = (random.random()*math.pi)    # current direction in radians

        # assign a random color to this agent
        # RGBA format: red green blue alpha -> alpha = transparency
        self.color = (random.randint(0,255), random.randint(0,255), random.randint(0,255), 255)

        # assign a sprite to this agent
        self.sprite = pyglet.shapes.Rectangle(x=self.x, y=self.y, width=AGENT_SCALE_FACTOR, height=AGENT_SCALE_FACTOR, color=self.color, batch=batch_agents)

        # we could consider agents with individual parameters, instead of using the global parameters for all agents (tangential)
        # self.sensor_offset = param_sensor_offset
        # self.sensor_angle = param_sensor_angle
        # self.turn_angle = param_turn_angle
        # ...

    # called every frame: update direction and position based on parameter values
    def on_update(self):
        self.update_direction()
        self.update_position()
    
    # decide on a new direction based on sensor data
    def update_direction(self):
        # acquire sensor data at 3 points (offset from the agent, fanned from left to right) 
        left = self.sense(-param_sensor_angle)
        center = self.sense(0)
        right = self.sense(+param_sensor_angle)
        
        # decide on a direction based on sensor data
        # update direction towards max sensed value by amount=param_turn_angle
        if (center > left and center > right):
            pass
        elif (center < left and center > right):
            if (np.random.rand() < 0.5): self.dir += param_turn_angle
        elif (left > right):
            self.dir += -param_turn_angle
        elif (right > left):
            self.dir += param_turn_angle

        # check if we want to apply drift (random angle modifier)
        if (np.random.rand() < param_drift_chance):
            self.dir += random.uniform(-param_drift_weight, param_drift_weight)

    # return the value of the trail_map at a point relative to ourselves (the agent)
    def sense(self, dir_offset):
        # check if wandering (return random value)
        # maybe more like "blind" at this sensor point
        if (np.random.rand() < param_wander_chance):
            return random.randint(-param_wander_weight, param_wander_weight)
        
        # dir_offset is the angle relative to our current direction
        angle = self.dir + dir_offset

        # get x and y coordinates of the point a certain angle and distance (param_sensor_offset) away from us 
        # x and y components of the point relative to ourselves
        x = math.floor(self.x + param_sensor_offset * math.cos(angle))
        y = math.floor(self.y + param_sensor_offset * math.sin(angle))

        # wrap x and y coordinates to contain them inside of the window (we don't want to go out of bounds)
        x = (x + window.width) % window.width
        y = (y + window.height) % window.height
        
        # # return the trail at this location
        return trail_map[y, x, :][3] # alpha channel (highest trail intensity)
        # return screen[y, x, :][3] # screen is the copy of trail_map that we want to draw
    
    # move self one step and update agent sprite
    def update_position(self):
        # calculate x and y components of current direction
        dx = math.cos(self.dir)
        dy = math.sin(self.dir)

        # this loops takes param_step_size steps in unit increments
        for i in range(param_step_size):
            self.deposit() # deposit trail at each step

            # update location by one pixel
            self.x += dx
            self.y += dy
            self.x = (self.x + window.width) % window.width
            self.y = (self.y + window.height) % window.height

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
class Environment(Observer):
    def __init__(self, subject):
        subject.push_handlers(self)

        # image_data draws to the screen
        self.image_data = pyglet.image.ImageData(
            WIDTH, HEIGHT, IMG_FORMAT, screen.tobytes(), pitch
        )
        
        # sprite is the visualization of the trail map
        self.sprite = pyglet.sprite.Sprite(self.image_data, batch=batch_trail)
    
    # called every frame by SimulationTimer: decay trail and update associated pixels 
    def on_update(self):
        global trail_map, screen # use the global variables

        # decay trails
        trail_map = np.uint8(trail_map*param_trail_decay)
        
        # update the trail image to be drawn by the window
        screen = trail_map
        self.image_data.set_data(IMG_FORMAT, pitch, screen.tobytes()) # turn the colors into bytes and store it as an image
        self.sprite.image = self.image_data # this is the sprite drawn by the window every frame

@window.event
def on_draw():
    # erase the previous frame drawing
    window.clear()

    # draw the trail map sprite before (underneath) the agent sprites
    if show_trail: batch_trail.draw()
    if show_agents: batch_agents.draw()

    # draw the gui on top of everything
    draw_gui()

# draw a simple "immediate mode" gui using imgui-bundle library
# define interface elements (text, checkboxes, sliders) to be drawn every frame
# the drawn interface elements are interactable and can manipulate the parameters of the simulation
def draw_gui():
    # global show_demo_window, counter, user_text
    global param_agents_number, param_step_size, param_max_time_scale_factor, param_sensor_offset, param_sensor_angle, param_turn_angle, param_time_step_factor, param_trail_decay, param_wander_chance, param_wander_weight, param_drift_chance, param_drift_weight, show_agents, show_trail

    # begin gui definition
    # everything between imgui.begin() and imgui.end() defines the gui like an ordered list of elements
    imgui.new_frame()
    imgui.begin("Parameter Palette")

    # checkboxes to toggle drawing of trail/agents
    _, show_trail = imgui.checkbox("Show Trail", show_trail)
    imgui.same_line()
    _, show_agents = imgui.checkbox("Show Agents", show_agents)

    # sliders to adjust simulation parameters
    changed_param_agents_number, param_agents_number = imgui.slider_int(
        "AGENTS_NUMBER", param_agents_number, v_min=0, v_max=5000
    )
    changed_param_step_size, param_step_size = imgui.slider_int(
        "STEP_SIZE", param_step_size, v_min=0, v_max=100
    )
    changed_param_sensor_angle, param_max_time_scale_factor = imgui.slider_float(
        "MAX_TIME_SCALE_FACTOR", param_max_time_scale_factor, v_min=0, v_max=10
    )
    changed_param_sensor_offset, param_sensor_offset = imgui.slider_int(
        "SENSOR_OFFSET", param_sensor_offset, v_min=-300, v_max=300
    )
    changed_param_sensor_angle, param_sensor_angle = imgui.slider_float(
        "SENSOR_ANGLE", param_sensor_angle, v_min=-math.pi, v_max=math.pi
    )
    changed_param_turn_angle, param_turn_angle = imgui.slider_float(
        "TURN_ANGLE", param_turn_angle, v_min=-math.pi, v_max=math.pi
    )
    changed_param_trail_decay, param_trail_decay = imgui.slider_float(
        "TRAIL_DECAY", param_trail_decay, v_min=0, v_max=1
    )
    changed_param_wander_chance, param_wander_chance = imgui.slider_float(
        "WANDER_CHANCE", param_wander_chance, v_min=0, v_max=1
    )
    changed_param_wander_weight, param_wander_weight = imgui.slider_int(
        "WANDER_WEIGHT", param_wander_weight, v_min=0, v_max=255
    )
    changed_param_drift_chance, param_drift_chance = imgui.slider_float(
        "DRIFT_CHANCE", param_drift_chance, v_min=0, v_max=1
    )
    changed_param_drift_weight, param_drift_weight = imgui.slider_float(
        "DRIFT_WEIGHT", param_drift_weight, v_min=-2*math.pi, v_max=2*math.pi
    )

    # end gui definition
    imgui.end()

    # draw the gui for this frame based on above definition
    imgui.render()
    renderer.render(imgui.get_draw_data())


# running the simulation loop
# example keyboard input
@window.event
def on_key_press(symbol, modifiers):
    # global restart_sim
    print('A key was pressed')
    pyglet.app.exit() 
    restart_sim() # doesn't work

@window.event
def on_key_press(symbol, modifiers):
    if symbol == key.A:
        print('The "A" key was pressed.')
    elif symbol == key.LEFT:
        print('The left arrow key was pressed.')
    elif symbol == key.ENTER:
        print('The enter key was pressed.')

# reset the simulation state (but not the parameters)
def restart_sim():
    pyglet.app.exit()

    # simulation_timer runs the main loop of the simulation
    # dt = delta time; amount of time elapsed between updates (1/frame_rate)
    # everything else in the simulation (Environment and Agents) updates when simulation_timer.tick() is called
    simulation_timer = SimulationTimer()
    def update_loop(dt):
        simulation_timer.tick()

    agents = np.empty(param_agents_number, Agent)
    for i in range(param_agents_number):
        agents[i] = Agent(simulation_timer)
    
    env = Environment(simulation_timer)

    
    pyglet.clock.schedule_interval(update_loop, 1/(FRAME_RATE*param_max_time_scale_factor))  # update at FRAME_RATE Hz (FRAME_RATE updates/second)
    pyglet.app.run()
    # print("wow")

# used for rendering gui later
imgui.create_context()
renderer = create_renderer(window)

# start the program
restart_sim()
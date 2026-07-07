import math
import random
import numpy as np
import pyglet
from pyglet.window import key
from pyglet.gl import *
from imgui_bundle import imgui
from imgui_bundle.python_backends.pyglet_backend import create_renderer

# disable texture filter
glEnable(GL_TEXTURE_2D)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

WIDTH = int(512*1.25)
HEIGHT = int(512*1.25)

FRAME_RATE = 60.0
TIME_STEP_FACTOR = 3.0
AGENT_SCALE_FACTOR = 1.0

param_time_step_factor = 1.0
param_agents_number = 1000
# AGENTS_COLOR = new Uint8Array([0, 0, 0]);
# param_agent_scale_factor = 1.0
param_sensor_offset = 10
param_sensor_angle = math.pi / 4
param_turn_angle = math.pi / 9
param_step_size = 1
param_max_time_scale_factor = 1
param_trail_decay = 0.95
param_wander_chance = 0.003
param_wander_weight = 124
param_drift_chance = 0.003
param_drift_weight = math.pi / 9
# random.seed(0)
window = pyglet.window.Window(WIDTH, HEIGHT)
batch_trail = pyglet.graphics.Batch()
batch_agents = pyglet.graphics.Batch()
batch_gui = pyglet.graphics.Batch()

imgui.create_context()

renderer = create_renderer(window)

# Application state tracking vars
show_demo_window = True
counter = 0
show_trail = True
show_agents = True


RGB_CHANNELS = 4
MAX_COLOR = 255
IMG_FORMAT = 'RGBA'
pitch = WIDTH * RGB_CHANNELS

screen = np.zeros(
    [HEIGHT, WIDTH, RGB_CHANNELS], dtype=np.uint8
)
pixel_screen = np.zeros(
    [HEIGHT, WIDTH, RGB_CHANNELS], dtype=np.uint8
)
trail_map = np.zeros(
    [HEIGHT, WIDTH, RGB_CHANNELS], dtype=np.uint8
)

# pyglet.gl.glClearColor(random.random(), random.random(), random.random(), 1.0)

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
class AgentTimer(pyglet.event.EventDispatcher):
    def tick(self):
        self.dispatch_event('on_update')

AgentTimer.register_event_type('on_update')

class Environment(Observer):
    def __init__(self, subject):
        subject.push_handlers(self)
    
    def on_update(self):
        global trail_map, screen

        trail_map = np.uint8(trail_map*param_trail_decay)
        screen = trail_map
        
        image_data.set_data(IMG_FORMAT, pitch, screen.tobytes())
        # pixel_image_data.set_data(IMG_FORMAT, pitch, pixel_screen.tobytes())
        # image_data.set_data(IMG_FORMAT, pitch, data)
        sprite.image = image_data
        # pixel_sprite.image = pixel_image_data

class Agent(Observer):
    def __init__(self, subject):
        subject.push_handlers(self)
        
        self.x = window.width / 2
        self.y = window.height / 2
        self.dir = math.pi
        self.color = (random.randint(0,255), random.randint(0,255), random.randint(0,255), 255)

        # self.x = random.randint(window.width // 2 - window.width // 12, window.width // 2 + window.width // 12)
        # self.y = random.randint(window.height // 2 - window.height // 12, window.height // 2 + window.height // 12)
        self.dir = (random.random()*2*math.pi)

        # self.sensor_offset = param_sensor_offset
        # self.sensor_angle = param_sensor_angle
        # self.turn_angle = param_turn_angle

        self.square = pyglet.shapes.Rectangle(x=self.x, y=self.y, width=AGENT_SCALE_FACTOR, height=AGENT_SCALE_FACTOR, color=self.color, batch=batch_agents)

    def on_update(self):
        self.update_direction()
        self.update_position()
        # self.square.x = self.x
        # self.square.y = self.y
    
    def update_direction(self):
        left = self.sense(-param_sensor_angle)
        center = self.sense(0)
        right = self.sense(+param_sensor_angle)
        
        if (center > left and center > right):
            # if (np.random.rand() < param_wander_chance): self.dir += random.uniform(-param_turn_angle, param_turn_angle)
            pass
        elif (center < left and center > right):
            if (np.random.rand() < 0.5): self.dir += param_turn_angle
        elif (left > right):
            self.dir += -param_turn_angle
        elif (right > left):
            self.dir += param_turn_angle

        if (np.random.rand() < param_drift_chance):
            self.dir += random.uniform(-param_drift_weight, param_drift_weight)

        # threeWays = [left, center - 1 , right]
        # minIndex = threeWays.index(min(threeWays))
        # self.dir += self.turn_angle * (minIndex - 1)
  
    def sense(self, dir_offset):
        angle = self.dir + dir_offset
        x = math.floor(self.x + param_sensor_offset * math.cos(angle))
        y = math.floor(self.y + param_sensor_offset * math.sin(angle))
        x = (x + window.width) % window.width
        y = (y + window.height) % window.height

        # return random.randint(0, 12)
        # return (x + y * window.width) * 4 # temp lol

        # index = (x + y * window.width)*4
        # return trail_map[index]
        # return max(screen[y, x, :])
        if (np.random.rand() < param_wander_chance):
            return random.randint(-param_wander_weight, param_wander_weight)
        return trail_map[x, y, :][3] # alpha channel (highest trail intensity)
        return screen[y, x, :][3] # alpha channel (highest trail intensity)
        # return max(trail_map[int(self.y)][int(self.x)][:])
    
    def update_position(self):
        dx = math.cos(self.dir)
        dy = math.sin(self.dir)
        for i in range(param_step_size):
            self.deposit()

            self.x += dx
            self.y += dy
            # if (random.random() < param_drift_chance): self.x *= random.uniform(-param_drift_weight, param_drift_weight)
            # if (random.random() < param_drift_chance): self.y *= random.uniform(-param_drift_weight, param_drift_weight)
            self.x = (self.x + window.width) % window.width
            self.y = (self.y + window.height) % window.height

            # index = math.floor(self.x) + math.floor(self.y) * window.width
        self.square.x = self.x
        self.square.y = self.y
    
    def deposit(self):
        # for i in range (STEP_SIZE):
        #     trail_map[int(self.y)-i][int(self.x)-i][:]  = self.color
        # trail_map[int(self.y)][int(self.x)][:]  = [0,255,0,255]
        trail_map[int(self.y)][int(self.x)][:]  = self.color

        # trail_map[self.get_index()] = 1.0


agents = np.empty(param_agents_number, Agent)
agent_timer = AgentTimer()

env = Environment(agent_timer)
for i in range(param_agents_number):
    agents[i] = Agent(agent_timer)

@window.event
def on_draw():
    window.clear()

    if show_trail: batch_trail.draw()
    if show_agents: batch_agents.draw()

    draw_gui()

# user_text = "Initial text"

def draw_gui():
    # global show_demo_window, counter, user_text
    global param_agents_number, param_step_size, param_max_time_scale_factor, param_sensor_offset, param_sensor_angle, param_turn_angle, param_time_step_factor, param_trail_decay, param_wander_chance, param_wander_weight, param_drift_chance, param_drift_weight, show_agents, show_trail

    imgui.new_frame()
    imgui.begin("Parameter Palette")
    # imgui.text("Adjust parameters here!")

    # Checkbox toggle for original demo window
    _, show_trail = imgui.checkbox("Show Trail", show_trail)
    imgui.same_line()
    _, show_agents = imgui.checkbox("Show Agents", show_agents)

    # Interactive Button logic
    # if imgui.button("Increment Counter"):
    #     counter += 1
    # imgui.same_line()
    # imgui.text(f"Button clicks: {counter}")
    # imgui.slider_int("AGENTS_NUMBER",)

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
        "SENSOR_ANGLE", param_sensor_angle, v_min=-2*math.pi, v_max=2*math.pi
    )
    changed_param_turn_angle, param_turn_angle = imgui.slider_float(
        "TURN_ANGLE", param_turn_angle, v_min=-2*math.pi, v_max=2*math.pi
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

    # imgui.spacing()

    # changed, user_text = imgui.input_text("Label Here", user_text)

    imgui.end()

    # If requested, display the engine standard Demo Window
    # if show_demo_window:
    #     imgui.show_demo_window()
    
    imgui.render()
    renderer.render(imgui.get_draw_data())

@window.event
def on_key_press(symbol, modifiers):
    print('A key was pressed')

@window.event
def on_key_press(symbol, modifiers):
    if symbol == key.A:
        print('The "A" key was pressed.')
    elif symbol == key.LEFT:
        print('The left arrow key was pressed.')
    elif symbol == key.ENTER:
        print('The enter key was pressed.')

# sprite = pyglet.sprite.Sprite(image)
# sprite.dx = 10.0

def update_loop(dt):
    agent_timer.tick()
    # for agent in agents:
    #     agent.update_direction()
    #     agent.update_position()

image_data = pyglet.image.ImageData(
    WIDTH, HEIGHT, IMG_FORMAT, screen.tobytes(), pitch
)
pixel_image_data = pyglet.image.ImageData(
    WIDTH, HEIGHT, IMG_FORMAT, pixel_screen.tobytes(), pitch
)
# Use a numpy array to store the pixels
# for i in range(WIDTH):
#     for j in range(HEIGHT):
#         screen[i, j, :] = round(trail_map[i + j * window.width]*MAX_COLOR)
# Flip the up coordinates
# data = np.flipud(screen).tobytes()
# If your pixels change you can use set_data
# image_data.set_data(IMG_FORMAT, pitch, data)
sprite = pyglet.sprite.Sprite(image_data, batch=batch_trail)
# pixel_sprite = pyglet.sprite.Sprite(image_data, batch=batch_agents)

def restart_sim():
    pyglet.clock.schedule_interval(update_loop, 1/(FRAME_RATE*param_max_time_scale_factor))  # update at FRAME_RATE Hz (FRAME_RATE updates/second)

restart_sim()
pyglet.app.run()
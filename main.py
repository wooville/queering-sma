import math
import random
import numpy as np
import pyglet
from pyglet.window import key
# from PIL import Image
from pyglet.gl import *
from imgui_bundle import imgui
from imgui_bundle.python_backends.pyglet_backend import create_renderer


# glEnable(GL_TEXTURE_2D)
# glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

WIDTH = int(512*1.25)
HEIGHT = int(512*1.25)

FRAME_RATE = 144.0
TIME_STEP_FACTOR = 4.0
AGENTS_NUMBER = 2500
# AGENTS_COLOR = new Uint8Array([0, 0, 0]);
AGENT_SCALE_FACTOR = 1.0
SENSOR_OFFSET = 10
SENSOR_ANGLE = math.pi / 4
TURN_ANGLE = math.pi / 9
STEP_SIZE = 1


param_time_step_factor = 1.0
param_agents_number = 2500
# AGENTS_COLOR = new Uint8Array([0, 0, 0]);
# param_agent_scale_factor = 1.0
param_sensor_offset = 10
param_sensor_angle = math.pi / 4
param_turn_angle = math.pi / 9
param_step_size = 1

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



RGB_CHANNELS = 4
MAX_COLOR = 255

screen = np.zeros(
    [HEIGHT, WIDTH, RGB_CHANNELS], dtype=np.uint8
)
pixel_screen = np.zeros(
    [HEIGHT, WIDTH, RGB_CHANNELS], dtype=np.uint8
)
IMG_FORMAT = 'RGBA'
pitch = WIDTH * RGB_CHANNELS

trail_map_test = np.zeros(
    [HEIGHT, WIDTH, RGB_CHANNELS], dtype=np.uint8
)

# pixel_map = np.empty(window.width*window.height)
# trail_map = np.empty(window.width*window.height)

# trail_map = np.empty(window.width*window.height*4)
# trail_map_2d = np.empty([window.width, window.height])

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
    def on_update(self):
        global trail_map
        global trail_map_test
        global screen
        # trail_map = trail_map-0.1
        # trail_map = np.round(trail_map*0.99, 2)
        trail_map_test = np.uint8(trail_map_test*0.92)
        # screen = np.round(screen*0.99, 2)
        screen = trail_map_test
        
        # trail_map = int(trail_map*10*0.9)/10
        # image_data = pyglet.image.ImageData(
            # WIDTH, HEIGHT, IMG_FORMAT, screen.tobytes(), pitch
        # )

        # print(np.where(trail_map > 0))
        # test = np.asarray(trail_map > 0).nonzero()[0]
        # for t in np.asarray(trail_map > 0).nonzero()[0]:
        #     # print(test.size)
        #     i = t//window.width
        #     j = t%window.width
        #     trail_decayed = trail_map[i + j * window.width]*0.9
        #     new_val = 0 if (math.isclose(0,trail_decayed, rel_tol=1e-3) or trail_decayed<0) else trail_decayed
        #     trail_map[i + j * window.width] = new_val
        #     screen[i, j, :] = new_val*MAX_COLOR

        # for t in np.where(pixel_map > 0)[0]:
        #     i = t//window.width
        #     j = t%window.width
        #     # trail_decayed = trail_map[i + j * window.width]*0.8
        #     # new_val = 0 if math.isclose(trail_decayed, 0) else trail_decayed
        #     # pixel_map[i + j * window.width] = 
        #     pixel_screen[i, j, :] = pixel_map[i + j * window.width]
        
        # Use a numpy array to store the pixels
        # for i in range(WIDTH):
        #     for j in range(HEIGHT):
        #         screen[j, i, :] = round(trail_map[math.floor(i) + math.floor(j) * window.width]*MAX_COLOR)
                # print(trail_map[math.floor(i) + math.floor(1) * window.width])
        # Flip the up coordinates
        # data = np.fliplr(screen).tobytes()
        # data = np.rot90(screen, k=1).tobytes()
        # data = np.flip(screen).tobytes()
        # If your pixels change you can use set_data
        image_data.set_data(IMG_FORMAT, pitch, screen.tobytes())
        # pixel_image_data.set_data(IMG_FORMAT, pitch, pixel_screen.tobytes())
        # image_data.set_data(IMG_FORMAT, pitch, data)
        sprite.image = image_data
        # pixel_sprite.image = pixel_image_data

class Agent(Observer):
    def __init__(self, subject):
        subject.push_handlers(self)
        
        # self.x = window.width / 2
        # self.y = window.height / 2
        # self.dir = math.pi
        self.color = (random.randint(0,255), random.randint(0,255), random.randint(0,255), 255)

        self.x = random.randint(window.width // 2 - window.width // 12, window.width // 2 + window.width // 12)
        self.y = random.randint(window.height // 2 - window.height // 12, window.height // 2 + window.height // 12)
        self.dir = (random.random()*2*math.pi)

        self.sensor_offset = SENSOR_OFFSET
        self.sensor_angle = SENSOR_ANGLE
        self.turn_angle = TURN_ANGLE

        # pixel_map[self.get_index()] = -1

        self.square = pyglet.shapes.Rectangle(x=self.x, y=self.y, width=AGENT_SCALE_FACTOR, height=AGENT_SCALE_FACTOR, color=self.color, batch=batch_agents)

    def get_index(self):
        return (math.floor(self.x) + math.floor(self.y) * window.width)*4

    def on_update(self):
        self.update_direction()
        self.update_position()
        # self.square.x = self.x
        # self.square.y = self.y
    
    def update_direction(self):
        left = self.sense(-self.sensor_angle)
        center = self.sense(0)
        right = self.sense(+self.sensor_angle)
        
        if (center > left and center > right):
            pass
        elif (center < left and center > right):
            if (np.random.rand() < 0.5): self.dir += self.turn_angle
        elif (left > right):
            self.dir += -self.turn_angle
        elif (right > left):
            self.dir += self.turn_angle


        # threeWays = [left, center - 1 , right]
        # minIndex = threeWays.index(min(threeWays))
        # self.dir += self.turn_angle * (minIndex - 1)
  
    def sense(self, dir_offset):
        angle = self.dir + dir_offset
        x = math.floor(self.x + self.sensor_offset * math.cos(angle))
        y = math.floor(self.y + self.sensor_offset * math.sin(angle))
        x = (x + window.width) % window.width
        y = (y + window.height) % window.height

        # return random.randint(0, 12)
        # return (x + y * window.width) * 4 # temp lol

        # index = (x + y * window.width)*4
        # return trail_map[index]
        return max(screen[x, y, :])
        # return max(trail_map_test[int(self.y)][int(self.x)][:])
    
    def update_position(self):
        # for i in range(STEP_SIZE):
        self.deposit()

        self.x += math.cos(self.dir)*STEP_SIZE
        self.y += math.sin(self.dir)*STEP_SIZE
        self.x = (self.x + window.width) % window.width
        self.y = (self.y + window.height) % window.height

        # index = math.floor(self.x) + math.floor(self.y) * window.width
        self.square.x = self.x
        self.square.y = self.y
    
    def deposit(self):
        # for i in range (STEP_SIZE):
        #     trail_map_test[int(self.y)-i][int(self.x)-i][:]  = self.color
        # trail_map_test[int(self.y)][int(self.x)][:]  = [0,255,0,255]
        trail_map_test[int(self.y)][int(self.x)][:]  = self.color

        # trail_map[self.get_index()] = 1.0


agents = np.empty(AGENTS_NUMBER, Agent)
agent_timer = AgentTimer()

env = Environment(agent_timer)
for i in range(AGENTS_NUMBER):
    agents[i] = Agent(agent_timer)

@window.event
def on_draw():
    window.clear()
    # image_data.blit(0, 0)
    batch_trail.draw()
    batch_agents.draw()
    # batch_gui.draw()
    # label.draw()

    imgui.new_frame()
    global show_demo_window, counter
    imgui.begin("Pyglet Integration Panel")
    imgui.text("Hello from Dear ImGui Bundle running inside Pyglet!")

    # Checkbox toggle for original demo window
    _, show_demo_window = imgui.checkbox("Show ImGui Demo Window", show_demo_window)
    
    # Interactive Button logic
    if imgui.button("Increment Counter"):
        counter += 1
    imgui.same_line()
    imgui.text(f"Button clicks: {counter}")
    # imgui.slider_int("AGENTS_NUMBER",)

    imgui.end()

    # If requested, display the engine standard Demo Window
    if show_demo_window:
        imgui.show_demo_window()

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

pyglet.clock.schedule_interval(update_loop, 1/(FRAME_RATE*TIME_STEP_FACTOR))  # update at FRAME_RATE Hz (FRAME_RATE updates/second)
pyglet.app.run()
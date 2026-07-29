# from . import pyglet
from . import random
from . import math
from . import numpy as np
from . import signal
from . import pyglet

# Abstract observer class
class Observer:
    def __init__(self, subject):
        subject.push_handlers(self)

# # The subject
# class SimulationTimer(pyglet.event.EventDispatcher):
#     def tick(self):
#         self.dispatch_event('on_update') # tell everyone to update

class QSMASimulation():
    def __init__(self, params, signals, batches):
        self.params = params
        # print(self.params)
        self.batch_trail = data['batches'][0]
        self.batch_agents = data['batches'][1]

        self.signal_sim_params_changed = signals['sim_params_changed']
        self.signal_sim_params_changed.connect(self.update_params)
        # SimulationTimer.register_event_type('on_update')
        
        self.restart()
    
    def update(self, dt):
        self.environment_map = np.uint8(self.environment_map*self.params["trail_decay"]*dt)
        for agent in self.agents:
            agent.update(dt)
        # print(self.environment_map.tobytes())
        # return {'environment_map': self.environment_map}

    def update_params(self, sender, **kw):
        # self.params = kw
        print(self.params)

    # reset the simulation state (but not the parameters)
    def restart(self):
        # reset simulation environment
        # image information
        self.width = self.params["width"]
        self.height = self.params["height"]
        self.RGB_CHANNELS = 4
        self.MAX_COLOR = 255
        self.IMG_FORMAT = 'RGBA'
        self.pitch = self.width * self.RGB_CHANNELS

        # our current QSMA relies on a spatial abstraction
        # ie, we are ultimately interpreting every input into an image (environment_map) to run our simulation on
        self.environment_map = np.zeros(
            [self.height, self.width, self.RGB_CHANNELS], dtype=np.uint8 # note that height/width are swapped, don't worry too much about it...
            )
        # create our agents according to parameters
        self.agents = np.empty(self.params["agents_number"], self.Agent)
        for i in range(self.params["agents_number"]):
            self.agents[i] = self.Agent(self.params, self.environment_map)

    # Here, we define the behaviour of each individual agent
    # When we run the program, we will create many of these agents that act based on our code here
    # Agents move and turn  based on information retrieved by sensing the self.env_map around them 
    class Agent(Observer):
        # every time we create an Agent, we first initialize it based on this function
        def __init__(self, params, environment_map):
            # this code spawns agents exactly in the middle of the window
            # self.x = window.width / 2
            # self.y = window.height / 2
            # self.direction = math.pi
            self.params = params
            self.environment_map = environment_map
            
            # Here, we initialize this individual agent's important variables (current position and direction)
            # These self.variable values are accessible in our other functions after this point
            # this code spawns agents randomly near the center of the window
            self.x = random.randint(environment_map.shape[0] // 2 - environment_map.shape[0] // 16, environment_map.shape[0] // 2 + environment_map.shape[0] // 16)
            self.y = random.randint(environment_map.shape[1] // 2 - environment_map.shape[1] // 16, environment_map.shape[1] // 2 + environment_map.shape[1] // 16)
            self.direction = (random.random()*math.pi)    # current direction in radians

            # assign a random color to this agent
            # RGBA format: Red Green Blue Alpha -> alpha = opacity
            self.color = (random.randint(0,255), random.randint(0,255), random.randint(0,255), 255)

            # assign a sprite to this agent (so we can draw it) and give it our (x,y) position, color
            # self.sprite = pyglet.shapes.Rectangle(x=self.x, y=self.y, width=AGENT_SCALE_FACTOR, height=AGENT_SCALE_FACTOR, color=self.color, batch=params["batch_agents"])

            # we could consider agents with individual parameters, instead of using the same global parameters for all agents (tangential)
            # self.sensor_offset = sim_params["sensor_offset"]
            # self.sensor_angle = sim_params["sensor_angle"]
            # self.turn_angle = sim_params["turn_angle"]
            # ...

        # called every frame: update direction and position based on global parameter values
        def update(self, dt):
            self.update_direction(dt)
            self.update_position(dt)
        
        # decide on a new direction based on sensor data
        def update_direction(self, dt):
            # acquire sensor data at 3 points (offset from the agent, fanned from left to right) 
            left = self.sense(-self.params["sensor_angle"]*math.pi)
            center = self.sense(0)
            right = self.sense(+self.params["sensor_angle"]*math.pi)
            
            # decide on a direction based on sensor data
            # update direction towards max sensed value by amount=sim_params["turn_angle"]
            if (center > left and center > right):
                pass
            elif (center < left and center > right):
                if (np.random.rand() < 0.5): self.direction += self.params["turn_angle"]*math.pi
            elif (left > right):
                self.direction += -self.params["turn_angle"]*math.pi
            elif (right > left):
                self.direction += self.params["turn_angle"]*math.pi

            # check if we want to apply drift (random angle modifier)
            if (np.random.rand() < self.params["drift_chance"]):
                self.direction += random.uniform(-self.params["drift_weight"]*math.pi, self.params["drift_weight"]*math.pi)

        # return the value of the self.environment_map at a point relative to ourselves (the agent)
        def sense(self, dir_offset):
            # check if wandering (return random value)
            # maybe more like "blind" at this sensor point
            if (np.random.rand() < self.params["wander_chance"]):
                return random.randint(-int(self.params["wander_weight"]*255), int(self.params["wander_weight"])*255)
            
            # dir_offset is the angle relative to our current direction
            angle = self.direction + dir_offset

            # get x and y coordinates of the point a certain angle and distance (sim_params["sensor_offset"]) away from us 
            # x and y components of the point relative to ourselves
            x = math.floor(self.x + self.params["sensor_offset"] * math.cos(angle))
            y = math.floor(self.y + self.params["sensor_offset"] * math.sin(angle))

            # wrap x and y coordinates to contain them inside of the window (we don't want to go out of bounds)
            width = self.environment_map.shape[0]
            height = self.environment_map.shape[1]
            x = (x + width) % width
            y = (y + height) % height
            
            # # return the trail at this location (specifically the opacity; we ignore the color)
            return self.environment_map[y, x, :][3] # [3] is the alpha channel (highest trail intensity)
        
        # move self one step and update agent sprite
        def update_position(self, dt):
            # calculate x and y components of current direction
            dx = math.cos(self.direction)
            dy = math.sin(self.direction)
            
            width = self.environment_map.shape[0]
            height = self.environment_map.shape[1]

            # this loops takes sim_params["step_size"] steps in unit increments
            for i in range(self.params["step_size"]):
                # update location by one pixel
                self.x += dx
                self.y += dy
                self.x = (self.x + width) % width
                self.y = (self.y + height) % height
                self.deposit() # deposit trail at each step

            # print(self.x)

            # update agent sprite with new location
            # self.sprite.x = self.x
            # self.sprite.y = self.y
        
        # deposit trail at current location (represented with a color value for visualization)
        def deposit(self):
            # this code makes all trails green
            # self.environment_map[int(self.y)][int(self.x)][:]  = [0,255,0,255]
            
            # if (pride_mode):
            self.environment_map[int(self.y)][int(self.x)][:] = self.color
            # print(self.environment_map)
            # else: self.environment_map[int(self.y)][int(self.x)][:] = param_trail_map_color

    # object class that updates the environment that agents interact with
    # we will create a single Environment, and all it does is update the value of the self.environment_map
    # class Environment():
    #     # def __init__(self):
    #         # image_data draws to the screen
    #         # self.image_data = pyglet.image.ImageData(
    #         #     self.width, self.height, IMG_FORMAT, self.environment_map.tobytes(), pitch
    #         # )
            
    #         # sprite is the visualization of the trail map
    #         # self.sprite = pyglet.sprite.Sprite(self.image_data, batch=batch_trail)
        
    #     # called every frame by SimulationTimer: decay trail and update associated pixels 
    #     def update(self):

    #         # decay trails, making sure that we're storing valid numbers into self.environment_map (our RGBA format)
    #         self.environment_map = np.uint8(self.environment_map*self.params["trail_decay"])

            # self.image_data.set_data(self.IMG_FORMAT, self.pitch, self.environment_map.tobytes()) # turn the colors into bytes and store it as an image
            # self.sprite.image = self.image_data # this is the sprite drawn by the window every frame
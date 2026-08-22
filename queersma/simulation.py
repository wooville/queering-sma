# from . import pyglet
from . import random
from . import math
from . import numpy as np
from . import signal
from . import pyglet
from .helpers import *

sim_params_default = {
    "width": 800,
    "height": 800,
    "depth": 800,
    "agents_number": 1000,
    "max_time_scale_factor": 1,
    "step_size": 10,
    "sensor_offset": 10,
    "sensor_angle": 0.25,
    "turn_angle": 0.111,
    "trail_decay": 0.15,
    "wander_chance": 0.003,
    "wander_weight": 0.5,
    "drift_chance": 0.05,
    "drift_weight": 0.08
}

class QSMASimulation():
    def __init__(self, signals, params = sim_params_default):
        self.params = params
        self.signals = signals
        # self.signals['agents_number_changed'].connect(self.update_agents_number)
        self.restart()
    
    def update(self, dt):
        decay_dt = dt*self.params["trail_decay"]

        self.environment_map *= (1-decay_dt)

        for agent in self.agents:
            if (agent is not None): agent.update(dt)

    # reset the simulation state (but not the parameters)
    def restart(self):
        # reset simulation environment
        # environment dimensions
        self.width = self.params["width"]
        self.height = self.params["height"]
        self.depth = self.params["depth"]

        # our current QSMA relies on a spatial abstraction
        # ie, we are ultimately interpreting every input into an image (environment_map) to run our simulation on
        # cube of uint8s
        self.environment_map = np.zeros(
            [self.width, self.height, self.depth], dtype=np.float32
        )

        # self.environment_map[:,:,:] = 255
        # create our agents according to parameters
        self.agents = np.empty(self.params["agents_number"], self.Agent)
        for i in range(self.params["agents_number"]):
            self.agents[i] = self.Agent(self.params, self.environment_map)

    # Here, we define the behaviour of each individual agent
    # When we run the program, we will create many of these agents that act based on our code here
    # Agents move and turn  based on information retrieved by sensing the self.env_map around them 
    class Agent():
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
            x = random.randint(environment_map.shape[0] // 2 - environment_map.shape[0] // 16, environment_map.shape[0] // 2 + environment_map.shape[0] // 16)
            y = random.randint(environment_map.shape[1] // 2 - environment_map.shape[1] // 16, environment_map.shape[1] // 2 + environment_map.shape[1] // 16)
            z = random.randint(environment_map.shape[2] // 2 - environment_map.shape[2] // 16, environment_map.shape[2] // 2 + environment_map.shape[2] // 16)
            self.position = np.asarray([x,y,z], dtype=np.int32)
            self.angle = [random.random()*math.pi*2, random.random()*math.pi*2] # x and y angle
            # self.theta = (random.random()*math.pi*2)    # current direction in radians
            # self.phi = (random.random()*math.pi*2)

            # assign a random color to this agent
            # RGBA format: Red Green Blue Alpha -> alpha = opacity
            self.color = (random.randint(0,255), random.randint(0,255), random.randint(0,255), 255)

        # called every frame: update direction and position based on global parameter values
        def update(self, dt):
            self.update_direction(dt)
            self.update_position(dt)
        
        # decide on a new direction based on sensor data
        def update_direction(self, dt):
            # Read trail
            leftAngle = self.angle[0] + self.params["sensor_angle"]
            rightAngle = self.angle[0] - self.params["sensor_angle"]
            topAngle = self.angle[1] + self.params["sensor_angle"]
            downAngle = self.angle[1] - self.params["sensor_angle"]

            # 3D
            frontPos =		self.position + np.asarray([math.cos(self.angle[1]) * math.cos(self.angle[0]), math.sin(self.angle[1]) * math.cos(self.angle[0]), math.sin(self.angle[0])]) * self.params["sensor_offset"]
            frontLeftPos =	self.position + np.asarray([math.cos(self.angle[0]) * math.cos(leftAngle), math.sin(self.angle[1]) * math.cos(leftAngle), math.sin(leftAngle)]) * self.params["sensor_offset"]
            frontRightPos =	self.position + np.asarray([math.cos(self.angle[1]) * math.cos(rightAngle), math.sin(self.angle[1]) * math.cos(rightAngle), math.sin(rightAngle)]) * self.params["sensor_offset"]
            frontTop =		self.position + np.asarray([math.cos(topAngle) * math.cos(self.angle[0]), math.sin(topAngle) * math.cos(self.angle[0]), math.sin(self.angle[0])]) * self.params["sensor_offset"]
            frontDown =		self.position + np.asarray([math.cos(downAngle) * math.cos(self.angle[0]), math.sin(downAngle) * math.cos(self.angle[0]), math.sin(self.angle[0])]) * self.params["sensor_offset"]
            
            F = self.sense_pos(frontPos)
            FL = self.sense_pos(frontLeftPos)
            FR = self.sense_pos(frontRightPos)
            FT = self.sense_pos(frontTop)
            FD = self.sense_pos(frontDown)

            # Get new position
            if (np.random.rand() < self.params["drift_chance"]):
                # RandomRotation
                self.angle[0] += self.params["turn_angle"]# * RandomSign(id.x + _AbsoluteTime)
                self.angle[1] += self.params["turn_angle"]# * RandomSign(id.x + 254 + _AbsoluteTime)
            else:
                maxIndex = 0
                maxValue = F
                trailThreshold = 1.0# - _TrailRepulsion

                if (FL > maxValue and FL < trailThreshold): 
                    maxIndex = 1
                    maxValue = FL
                if (FR > maxValue and FR < trailThreshold):
                    maxIndex = 2
                    maxValue = FR
                if (FT > maxValue and FT < trailThreshold):
                    maxIndex = 3
                    maxValue = FT
                if (FD > maxValue and FD < trailThreshold):
                    maxIndex = 4
                    maxValue = FD

                if (maxIndex == 0 and F >= trailThreshold):
                    self.angle[0] += self.params["turn_angle"]# * RandomSign(id.x + _AbsoluteTime)
                    self.angle[1] += self.params["turn_angle"]# * RandomSign(id.x + 254 + _AbsoluteTime)
                if (maxIndex == 1): self.angle[0] += self.params["turn_angle"]
                if (maxIndex == 2): self.angle[0] -= self.params["turn_angle"]
                if (maxIndex == 3): self.angle[1] += self.params["turn_angle"]
                if (maxIndex == 4): self.angle[1] -= self.params["turn_angle"]

        def sense_pos(self, pos):
            width = self.environment_map.shape[0]
            height = self.environment_map.shape[1]
            depth = self.environment_map.shape[2]

            # Bilinear filtering + wrap
            x = mod(int(pos[0]),width)
            y = mod(int(pos[1]),height)
            z = mod(int(pos[2]),depth)

            fx = pos[0] - x
            fy = pos[1] - y
            fz = pos[2] - z

            xp1 = min(width - 1, x + 1)
            yp1 = min(height - 1, y + 1)
            zp1 = min(depth - 1, z + 1)

            x0 = self.environment_map[x, y, z] * (1.0 - fx) + self.environment_map[xp1, y, z] * fx
            x1 = self.environment_map[x, y, zp1] * (1.0 - fx) + self.environment_map[xp1, y, zp1] * fx

            x2 = self.environment_map[x, yp1, z] * (1.0 - fx) + self.environment_map[xp1, yp1, z] * fx
            x3 = self.environment_map[x, yp1, zp1] * (1.0 - fx) + self.environment_map[xp1, yp1, zp1] * fx

            z0 = x0 * (1.0 - fz) + x1 * fz
            z1 = x2 * (1.0 - fz) + x3 * fz

            return z0 * (1.0 - fy) + z1 * fy
        
        # move self one step and update agent sprite
        def update_position(self, dt):
            newPos = self.position + np.asarray([math.cos(self.angle[1]) * math.cos(self.angle[0]), math.sin(self.angle[1]) * math.cos(self.angle[0]), math.sin(self.angle[0])]) * self.params["step_size"]

            # Check boundaries
            # 3D Cube
            width = self.environment_map.shape[0]
            height = self.environment_map.shape[1]
            depth = self.environment_map.shape[2]
            if (newPos[0] > width - 1): newPos[0] = 0
            if (newPos[1] > height - 1): newPos[1] = 0
            if (newPos[2] > depth - 1): newPos[2] = 0
            if (newPos[0] < 0): newPos[0] = width - 1
            if (newPos[1] < 0): newPos[1] = height - 1
            if (newPos[2] < 0): newPos[2] = depth - 1

            # 3D Sphere
            # inside = inside_sphere(newPos, _Size * 0.5f, _Size.x * 0.5);
            # RandomRotation
            # self.angle[0] += (self.params["turn_angle"]# * RandomSign(id.x + _AbsoluteTime)) * (1 - inside);
            # self.angle[1] += (self.params["turn_angle"]# * RandomSign(id.x + 254 + _AbsoluteTime)) * (1 - inside);

            # newPos = newPos * inside + pos * (1 - inside);

            # Move particule
            self.velocity = newPos - self.position
            self.position = newPos
            # self.angle = angle
            # _ParticleBuffer[id.x].color = color;

            # Update trail
            self.deposit(newPos)#, min(SampleDensityFromPosition(newPos) + _ParticleBuffer[id.x].color, 1))
        
        # deposit trail at point (x, y) (represented with a color value for visualization)
        def deposit(self, pos):
            self.environment_map[int(pos[0])][int(pos[1])][int(pos[2])] = self.color[2]
            # self.environment_map[int(y)][int(x)][0] += 
            # self.environment_map[int(y)][int(x)][0] += 
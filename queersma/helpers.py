from . import json
from . import numpy as np
from . import math

def read_json(path):
    with open(path, "r") as f:
        data = json.load(f)
        return data

def write_json(data, path):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

def get_points_integer(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    points = []
    
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy

    while True:
        points.append((x1, y1))
        if x1 == x2 and y1 == y2:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy
            
    return points

def rotate_quaternion(v, a, angle):
    result = math.cos(angle) * v + math.sin(angle) * (np.cross(a, v)) + np.dot(a, v) * (1 - math.cos(angle)) * a
    return result

def mod(a, b):
     return a - b * math.floor(a / b);

# //Return 1 if v inside the sphere, 0 otherwise
def inside_sphere(v, center, radius):
	position = v - center
	return (np.heaviside(radius, np.linalg.norm(position)) + 1.0) % 2.0

# def update_agent2(self, dt):
#     # // Get vector which points in the current particle's direction 
#     center_axis = np.asarray([math.sin(self.theta) * math.cos(self.phi), math.cos(self.theta), math.sin(self.theta) * math.sin(self.phi)])
#     width = self.environment_map.shape[0]
#     height = self.environment_map.shape[1]
#     depth = self.environment_map.shape[2]
    
#     # // Get base vector which points away from the current particle's direction and will be used
#     # // to sample environment in other directions
#     sense_theta = self.theta - self.params["sensor_angle"]
#     off_center_base_dir = np.asarray([math.sin(sense_theta) * math.cos(self.phi), math.cos(sense_theta), math.sin(sense_theta) * math.sin(self.phi)])

#     # // Sample environment straight ahead
#     p = np.asarray([self.x, self.y, self.z], dtype=np.int32)
#     center_sense_pos = center_axis * self.params["sensor_offset"]
#     # // Sample environment away from the center axis and store max values.
#     center_sense_pos = center_sense_pos.astype(np.int32) + p
#     # print(center_sense_pos)
#     max_value = self.environment_map[mod(center_sense_pos[0], width), mod(center_sense_pos[1], height), mod(center_sense_pos[2], depth)]
#     # max_value = self.environment_map[center_sense_pos.astype(np.int32) + p]
#     max_value_count = 1
#     SAMPLE_POINTS = 8
#     max_values = np.zeros(SAMPLE_POINTS + 1) # = {0, 0, 0, 0, 0, 0, 0, 0, 0};
#     max_values[0] = 0
#     # start_angle = random(idx * 42) * 3.1415 - math.pi/2
#     start_angle = (random.random()*math.pi)
#     for i in range (1, SAMPLE_POINTS):
#         angle = start_angle + math.pi * 2.0 / (SAMPLE_POINTS) * i
#         sense_position = rotate_quaternion(off_center_base_dir, center_axis, angle) * self.params["sensor_offset"] + p
#         sense_position = sense_position.astype(np.int32)
#         stuff = self.environment_map[mod(sense_position[0], width), mod(sense_position[1], height), mod(sense_position[2], depth)]
#         # print(stuff)
#         if (stuff > max_value):
#             max_value_count = 1
#             max_value = stuff
#             max_values[0] = i
#         elif (stuff == max_value):
#             max_value_count += 1
#             max_values[max_value_count] = i

#     # random_max_value_direction = wang_hash(idx * uint(x) * uint(y) * uint(z)) % max_value_count;
#     direction = np.max(max_values)
#     theta_turn = self.theta - self.params["turn_angle"]
#     off_center_base_dir_turn = np.asarray([math.sin(theta_turn) * math.cos(self.phi), math.cos(theta_turn), math.sin(theta_turn) * math.sin(self.phi)])
#     if (direction > 0):
#         best_direction = rotate_quaternion(off_center_base_dir_turn, center_axis, direction * math.pi * 2.0 / float(SAMPLE_POINTS) + start_angle)
#         self.phi = math.atan2(best_direction[2], best_direction[0])
#         self.theta = math.acos(best_direction[1] / np.linalg.norm(best_direction))

#     center_attraction = 1

#     to_center = np.asarray([width  / 2.0 - self.x, height / 2.0 - self.y, depth / 2.0 - self.z])
#     d_center = np.linalg.norm(to_center)
#     d_c_turn = np.clip((d_center - 50.0) / 150.0, 0, 1) * center_attraction;
#     dir1 = np.asarray([math.sin(self.theta) * math.cos(self.phi), math.cos(self.theta), math.sin(self.theta) * math.sin(self.phi)])
#     center_dir = np.linalg.norm(to_center)
#     center_angle = np.acos(np.dot(dir1, center_dir))
#     st = 0.1 * d_c_turn
#     dir1 = np.sin((1 - st) * center_angle) / np.sin(center_angle) * dir1 + np.sin(st * center_angle) / np.sin(center_angle) * center_dir
#     dir1_mag = np.linalg.norm(dir1)
#     if (dir1_mag > 0.0 and (dir1[2] != 0.0 or dir1[0] != 0.0)):
#         self.theta = math.acos(dir1[1] / dir1_mag)
#         self.phi = math.atan2(dir1[2], dir1[0])

#     # // Make a step
#     dp = np.asarray([math.sin(self.theta) * math.cos(self.phi), math.cos(self.theta), math.sin(self.theta) * math.sin(self.phi)]) * self.params["step_size"] # * (move_sense_offset + max_value * move_sense_coef)
#     x = self.x + dp[0]
#     y = self.y + dp[1]
#     z = self.z + dp[2]

#     # // Keep the particle inside environment

#     self.x = mod(x, width)
#     self.y = mod(y, height)
#     self.z = mod(z, depth)

#     # // Check for collisions
#     # val = 0;
#     # InterlockedCompareExchange(tex_occ[uint3(x, y, z)], 0, uint(collision), val);
#     # if (val == 1.0) {
#     #     x = particles_x[idx];
#     #     y = particles_y[idx];
#     #     z = particles_z[idx];
#     #     t = acos(2 * float(wang_hash(idx * uint(x) * uint(y) * uint(z) + 4) % 1000) / 1000.0 - 1);
#     #     ph = float(wang_hash(idx * uint(x) * uint(y) * uint(z) + 12) % 1000) / 1000.0 * 3.1415 * 2.0;
#     # }

#     # Update particle state
#     # particles_x[idx] = x
#     # particles_y[idx] = y
#     # particles_z[idx] = z
#     # particles_theta[idx] = t
#     # particles_phi[idx] = ph

#     self.deposit(self.x, self.y, self.z)

### EXTRAS
# this code makes the background of the window a random color
# pyglet.gl.glClearColor(random.random(), random.random(), random.random(), 1.0)

# unused multimedia functions
# image = pyglet.resource.image('kitten.jpg')
# music = pyglet.resource.media('music.mp3')
# music.play()
# sound = pyglet.resource.media('shot.wav', streaming=False)
# sound.play()

# create signals using Blinker library
# can use signals to communicate between QSMA modules
# self.signals = {
#     'sim_params_changed': signal('sim_params_changed')
#     }

# senses a line from here to there instead of a point
# def sense2(self, dir_offset):
#     # check if wandering (return random value)
#     # maybe more like "blind" at this sensor point
#     if (np.random.rand() < self.params["wander_chance"]):
#         return random.randint(-int(self.params["wander_weight"]*255), int(self.params["wander_weight"])*255)
    
#     # dir_offset is the angle relative to our current direction
#     angle = self.direction + dir_offset

#     # get x and y coordinates of the point a certain angle and distance (sim_params["sensor_offset"]) away from us 
#     # x and y components of the point relative to ourselves
#     x = math.floor(self.x + self.params["sensor_offset"] * math.cos(angle))
#     y = math.floor(self.y + self.params["sensor_offset"] * math.sin(angle))

#     # wrap x and y coordinates to contain them inside of the window (we don't want to go out of bounds)
#     width = self.environment_map.shape[0]
#     height = self.environment_map.shape[1]
#     x = (x + width) % width
#     y = (y + height) % height

#     # sense at every discrete point in the straight line between here and there
#     # very computationally expensive at this scale
#     sense_pts = get_points_integer([int(self.x), int(self.y)], [int(x), int(y)])
#     ret = 0
#     for p in sense_pts:
#         ret = np.uint8(max(ret, self.environment_map[p[1], p[0], :][3]))

#     return ret
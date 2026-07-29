import json

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
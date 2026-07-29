import json

def read_json(path):
    with open(path, "r") as f:
        data = json.load(f)
        return data

def write_json(data, path):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

### EXTRAS
# this code makes the background of the window a random color
# pyglet.gl.glClearColor(random.random(), random.random(), random.random(), 1.0)

# unused multimedia functions
# image = pyglet.resource.image('kitten.jpg')
# music = pyglet.resource.media('music.mp3')
# music.play()
# sound = pyglet.resource.media('shot.wav', streaming=False)
# sound.play()
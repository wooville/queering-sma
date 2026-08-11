from . import signal
from . import pyglet
from . import numpy as np
from . import math
from . import random
from . import imgui, create_renderer
from . import asyncio
from . import queue
from . import sys
from . import sounddevice as sd
from . import threading

from .helpers import write_json
from pyglet.window import key
from pyglet.gl import *
from pyglet.math import Mat4, Vec3
from typing import override

AGENT_SCALE_FACTOR = 1.0    # scale of drawn agent sprites (does not affect logic)

class QSMAWindow(pyglet.window.Window):
    def __init__(self, sim, signals, width, height, title, resizable):
        super().__init__(width, height, title, resizable)
        
        self.sim = sim
        self.signals = signals

        # self.signals['agents_number_changed'].connect(self.update_agent_sprites)
        
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
        self.trail_sprite = pyglet.sprite.Sprite(self.image_data, batch=self.batch_trail)
        
        self.agent_sprites = np.empty(self.sim.params["agents_number"], pyglet.shapes.Rectangle)
        for i in range(self.sim.agents.size):
            a = self.sim.agents[i]
            self.agent_sprites[i]=pyglet.shapes.Rectangle(x=a.x, y=a.y, width=AGENT_SCALE_FACTOR, height=AGENT_SCALE_FACTOR, color=a.color, batch=self.batch_agents)

        self.show_trail = True
        self.show_agents = True
        self.show_fps = True

        # Setup visual elements
        self.fps_display = pyglet.window.FPSDisplay(window=self)
        imgui.create_context()
        self.renderer = create_renderer(self)

        # scale up the gui (text + widget padding/sizes) for readability on HiDPI displays
        self.UI_SCALE = 1.25
        imgui.get_style().font_scale_main = self.UI_SCALE
        imgui.get_style().scale_all_sizes(self.UI_SCALE)
        
        self.setup_input_streams()

    def setup_input_streams(self):
        self.async_loop = asyncio.new_event_loop()
        threading.Thread(target=self.start_async_loop, args=(self.async_loop,), daemon=True).start()
    
    def start_async_loop(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    async def audio_stream_processor(self, sample_rate=44100, block_size=2048, channels=1):
        """Asynchronously captures and processes audio blocks without blocking the event loop."""
        loop = asyncio.get_running_loop()
        
        # Thread-safe FIFO queue to hold audio blocks moving from the OS thread to the async loop
        audio_queue = queue.Queue()

        # this is the callback function we will pass to the audio stream
        def sync_audio_callback(indata, outdata, frames, time, status):
            """Low-level callback executed by PortAudio in a separate OS thread."""
            if status:
                print(f"Status flag raised: {status}", file=sys.stderr)
            
            # Safely hand over a copy of the input buffer to our thread-safe queue
            # For a full duplex loopback, we also write the incoming data to the output buffer
            outdata[:] = indata
            
            pyglet.clock.schedule_once(lambda dt: self.update_audio_effect(indata), 0)
            # Push the data block into the queue and wake up the async event loop safely
            loop.call_soon_threadsafe(audio_queue.put_nowait, indata.copy())

        # Initialize the sounddevice Stream
        stream = sd.Stream(
            samplerate=sample_rate,
            blocksize=block_size,
            channels=channels,
            callback=sync_audio_callback
        )

        # Use the context manager to automatically open and close the stream safely
        with stream:
            print("Async audio stream started. Press Ctrl+C to stop.")
            while True:
                try:
                    # Retrieve a data block from the thread-safe queue
                    # We use a small timeout so the loop yields control frequently
                    data_block = await loop.run_in_executor(
                        None, audio_queue.get, True, 0.1
                    )
                except queue.Empty:
                    # Yield control to the async loop if no new audio block is ready yet
                    await asyncio.sleep(0.001)
                    continue

                # --- YOUR ASYNC PROCESSING GOES HERE ---
                # You can send 'data_block' to an async WebSocket, run real-time DSP, 
                # or pass it to an AI speech-to-text API without freezing your app.
                volume_norm = float(data_block.max())
                print(f"Captured audio block | Max volume: {volume_norm:.4f}", end="\r")

    async def input_stream_mic(self):
        try:
            await self.audio_stream_processor()
        except asyncio.CancelledError:
            print("\nStream cancelled.")

    def update_audio_effect(self, data):
        volume_norm = np.linalg.norm(data)
        # self.sim.params["step_size"] = int(100*volume_norm)+10
        self.sim.params["drift_chance"] = volume_norm
        self.sim.params["agents_number"] = int(5000*volume_norm+500)
        # self.sim.agents
        self.update_agents()

        # self.sim.environment_map[:] = np.uint8(self.sim.environment_map*(volume_norm+1))
        # ... whatever you want to do with audio here!
        # pyglet.gl.glClearColor(volume_norm, volume_norm, volume_norm, volume_norm)
    
    # the window executes this function when we press any key
    @override
    def on_key_press(self, symbol, modifiers):
        if symbol == key.R:
            print('Restarting simulation!')
            self.sim.restart()
        if symbol == key.F:
            print('FPS display toggled')
            self.show_fps = not self.show_fps
        elif symbol == key.ENTER:
            print('Microphone input stream running')
            asyncio.run_coroutine_threadsafe(self.input_stream_mic(), self.async_loop)
    
    @override
    def on_draw(self):
        # erase the previous frame drawing
        self.clear()
        
        # the simulation canvas is a sim.width x sim.height area; scale it to fill
        # the window (preserving aspect ratio) and center whatever's left over
        scale = min(self.width / self.sim.width, self.height / self.sim.height)
        offset_x = (self.width - self.sim.width * scale) / 2
        offset_y = (self.height - self.sim.height * scale) / 2
        self.view = Mat4.from_translation(Vec3(offset_x, offset_y, 0)) @ Mat4.from_scale(Vec3(scale, scale, 1))

        self.image_data.set_data(self.IMG_FORMAT, self.pitch, self.sim.environment_map.tobytes()) # turn the colors into bytes and store it as an image
        self.trail_sprite.image = self.image_data

        # self.update_agents()
        for i in range(len(self.sim.agents)):
            if (self.agent_sprites[i] is not None):
                # print(len(self.sim.agents))
                self.agent_sprites[i].x = self.sim.agents[i].x
                self.agent_sprites[i].y = self.sim.agents[i].y

        # draw the trail map sprite before (underneath) the agent sprites
        if self.show_trail: self.batch_trail.draw()
        if self.show_agents: self.batch_agents.draw()

        # reset the view so the fps display and gui aren't shifted by the offset
        self.view = Mat4()

        if self.show_fps: self.fps_display.draw()
        self.draw_gui()

    # draw a simple "immediate mode" gui using imgui-bundle library
    # define interface elements (text, checkboxes, sliders) to be drawn every frame
    # the drawn interface elements are interactable and can manipulate the parameters of the simulation
    def draw_gui(self):
        # begin gui definition
        # everything between imgui.begin() and imgui.end() defines the gui like an ordered list of elements
        imgui.new_frame()
        imgui.begin("Parameter Palette")
        # for param in self.core_params

        # checkboxes to toggle drawing of trail/agents
        _, self.show_trail = imgui.checkbox("Show Trail", self.show_trail)
        imgui.same_line()
        _, self.show_agents = imgui.checkbox("Show Agents", self.show_agents)

        if imgui.button("RESET SIM"):
            print('Restarting simulation!')
            self.sim.restart()

        # sliders to adjust simulation parameters
        agents_number_changed, self.sim.params["agents_number"] = imgui.slider_int(
            "AGENTS_NUMBER", self.sim.params["agents_number"], v_min=0, v_max=10000
        )
        _, self.sim.params["step_size"] = imgui.slider_int(
            "STEP_SIZE", self.sim.params["step_size"], v_min=0, v_max=1000
        )
        _, self.sim.params["max_time_scale_factor"] = imgui.slider_float(
            "MAX_TIME_SCALE_FACTOR", self.sim.params["max_time_scale_factor"], v_min=0.5, v_max=10
        )
        _, self.sim.params["sensor_offset"] = imgui.slider_int(
            "SENSOR_OFFSET", self.sim.params["sensor_offset"], v_min=-300, v_max=300
        )
        _, self.sim.params["sensor_angle"] = imgui.slider_float(
            "SENSOR_ANGLE", self.sim.params["sensor_angle"], v_min=-math.pi, v_max=math.pi
        )
        _, self.sim.params["turn_angle"] = imgui.slider_float(
            "TURN_ANGLE", self.sim.params["turn_angle"], v_min=-math.pi, v_max=math.pi
        )
        _, self.sim.params["trail_decay"] = imgui.slider_float(
            "TRAIL_DECAY", self.sim.params["trail_decay"], v_min=-1, v_max=5
        )
        _, self.sim.params["wander_chance"] = imgui.slider_float(
            "WANDER_CHANCE", self.sim.params["wander_chance"], v_min=0, v_max=1
        )
        _, self.sim.params["wander_weight"] = imgui.slider_float(
            "WANDER_WEIGHT", self.sim.params["wander_weight"], v_min=0, v_max=1
        )
        _, self.sim.params["drift_chance"] = imgui.slider_float(
            "DRIFT_CHANCE", self.sim.params["drift_chance"], v_min=0, v_max=1
        )
        _, self.sim.params["drift_weight"] = imgui.slider_float(
            "DRIFT_WEIGHT", self.sim.params["drift_weight"], v_min=-1, v_max=1
        )

        if imgui.button("SAVE PARAMS"):
            write_json(self.core_params, self.PARAMS_FILE_WRITE)
            print("Parameters saved into ", self.PARAMS_FILE_WRITE)

        if agents_number_changed:
            pyglet.clock.schedule_once(lambda dt: self.update_agents(), 0)

        # end gui definition
        imgui.end()

        # draw the gui for this frame based on above definition
        imgui.render()
        self.renderer.render(imgui.get_draw_data())

    def update_agents(self):
        diff = self.sim.agents.size-self.sim.params["agents_number"]

        if (diff>0):
            self.sim.agents = np.delete(self.sim.agents, np.s_[-abs(diff):-1])
            # self.sim.add_agents(diff)
            self.agent_sprites = np.delete(self.agent_sprites, np.s_[-abs(diff):-1])
        elif (diff<0):
            for i in range(abs(diff)):
                new_agent = self.sim.Agent(self.sim.params, self.sim.environment_map)
                self.sim.agents = np.append(self.sim.agents, new_agent)
                self.agent_sprites = np.append(self.agent_sprites, pyglet.shapes.Rectangle(x=new_agent.x, y=new_agent.y, width=AGENT_SCALE_FACTOR, height=AGENT_SCALE_FACTOR, color=new_agent.color, batch=self.batch_agents))
            # new_agent = self.sim.Agent(self.sim.params, self.sim.environment_map)
            # self.sim.add_agents(diff)
            

    # def update_agent_sprites(self, sender, **kw):
    #     self.agent_sprites = np.empty(int(self.sim.params["agents_number"]),pyglet.shapes.Rectangle)
    #     diff = self.agent_sprites.size-self.sim.params["agents_number"]

    #     # if (diff<0):
    #     #     self.agent_sprites = np.delete(self.agents, np.s_[-abs(diff):-1])
    #     # else
    #     for i in range(abs(diff)):
    #         if (diff<0):
    #             self.agent_sprites = np.delete(self.agents,-i)
    #         else:
    #             a = self.sim.agents[i]
    #             self.agent_sprites = np.append(self.agent_sprites, pyglet.shapes.Rectangle(x=a.x, y=a.y, width=AGENT_SCALE_FACTOR, height=AGENT_SCALE_FACTOR, color=a.color, batch=self.batch_agents))
            # print(self.agent_sprites.size)
            # self.agent_sprites = np.reshape(self.agents, self.params["agents_number"])
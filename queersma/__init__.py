# from .window import *
# from .simulation import *
# from .helpers import *

import os
import platform
current_os = platform.system()
if (current_os == "Linux"): os.environ.setdefault("PYOPENGL_PLATFORM", "x11")

import multiprocessing

import asyncio
import queue
import sys
import sounddevice
import threading

import math
import random
import numpy
import sounddevice

import blinker
from blinker import signal

import pyglet
if current_os == "Windows":
    pyglet.options.dpi_scaling = "real"
elif current_os == "Darwin":
    pyglet.options.dpi_scaling = "scaled"
elif current_os == "Linux":
    pyglet.options.dpi_scaling = "real"

# from pyglet.window import key
# from pyglet.gl import *
# from pyglet.math import Mat4, Vec3
# from imgui_bundle import imgui
# from imgui_bundle.python_backends.pyglet_backend import create_renderer
from imgui_bundle import imgui, immapp
from imgui_bundle.python_backends.pyglet_backend import create_renderer
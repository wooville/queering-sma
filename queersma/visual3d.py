from . import time
from . import viser
from . import trimesh
from . import numpy as np
from .helpers import *

class QSMAVisual3D():
    def __init__(self, sim):
        self.sim = sim
        # rng = np.random.default_rng()
        server = viser.ViserServer()
        
        # Add the point cloud to the scene.
        agents_pcd = server.scene.add_point_cloud(
            name="/agents_cloud",
            position=(0,0,0),
            points=np.array([agent.position for agent in self.sim.agents]),
            colors=np.array([[agent.color[0], agent.color[1], agent.color[2]] for agent in self.sim.agents]),
            point_size=1,
            scale=1
        )

        print("Open your browser to http://localhost:8080")
        print("Press Ctrl+C to exit")

        # I was trying to draw line segments
        # agent_points_buffer = agents_pcd.points
        # colors = rng.integers(low=1, high=255, size=(1000, 2, 3))
        while True:
            self.sim.update(1/60)
            # agents_pcd.points = np.array([[agent.x, agent.y, agent.z] for agent in self.sim.agents])
            agents_pcd.points = np.array([agent.position for agent in self.sim.agents])
            
            # print(np.stack([agents_pcd.points,agent_points_buffer], 1).shape)
            # server.scene.add_line_segments(
            #     "/trail_segments",
            #     points=np.stack([agents_pcd.points,agent_points_buffer], 1),
            #     colors=colors,
            #     thickness=0.03,
            # )

            time.sleep(1/60)
from . import time
from . import viser
from . import trimesh
from . import numpy as np
from .helpers import *

class QSMAVisual3D():
    def __init__(self, sim):
        self.sim = sim
        server = viser.ViserServer()
        
        # Add the point cloud of agents to the scene
        agents_pcd = server.scene.add_point_cloud(
            name="/agents_cloud",
            position=(0,0,0),
            points=np.array([agent.position for agent in self.sim.agents]),
            colors=np.array([[agent.color[0], agent.color[1], agent.color[2]] for agent in self.sim.agents]),
            point_size=1,
            scale=3,
            point_shape='circle'
        )

        # env_row, env_col, env_depth = np.indices((self.sim.width,self.sim.height,self.sim.depth))
        # instantiate trail cloud
        env_pts = np.argwhere(self.sim.environment_map>60)
        env_pcd = server.scene.add_point_cloud(
                    name="/environment_cloud",
                    position=(0,0,0),
                    points=env_pts,
                    colors=env_pts,
                    point_size=0.5,
                    scale=3,
                    point_shape='sparkle'
                )

        print("Open your browser to http://localhost:8080")
        print("Press Ctrl+C to exit")

        # currently serves as the main update loop for the simulation
        while True:
            self.sim.update(1/60)

            # only render trails of intensity > threshold -> grab those pts
            env_pts = np.argwhere(self.sim.environment_map>120)

            # update rendered trails
            env_pcd.points = np.array([[p[0], p[1], p[2]] for p in env_pts])
            env_pcd.colors = np.array([[0, self.sim.environment_map[p[0], p[1], p[2]], 0] for p in env_pts])

            # update rendered agent positions
            agents_pcd.points = np.array([agent.position for agent in self.sim.agents])

            time.sleep(1/60)
from . import time
from . import viser
from . import trimesh
from . import numpy as np
from .helpers import *

class QSMAVisual3D():
    def __init__(self, sim):
        self.sim = sim
        rng = np.random.default_rng()
        server = viser.ViserServer()
        
        # Add the point cloud to the scene.
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

        # I was trying to draw line segments
        # agent_points_buffer = agents_pcd.points
        # colors = rng.integers(low=1, high=255, size=(1000, 2, 3))
        while True:
            # agent_points_buffer = agents_pcd.points
            self.sim.update(1/60)
            # print(np.nonzero(self.sim.environment_map))
            env_pts = np.argwhere(self.sim.environment_map>120)
            # print(env_pts.shape)
            env_pcd.points = np.array([[p[0], p[1], p[2]] for p in env_pts])
            env_pcd.colors = np.array([[0, self.sim.environment_map[p[0], p[1], p[2]], 0] for p in env_pts])

            # agents_pcd.points = np.array([[agent.x, agent.y, agent.z] for agent in self.sim.agents])
            agents_pcd.points = np.array([agent.position for agent in self.sim.agents])
            # env_pcd.colors = np.array([[p, p, p] for p in self.sim.environment_map])

            # print(np.stack([agents_pcd.points,agent_points_buffer], 1).shape)
            # server.scene.add_line_segments(
            #     "/trail_segments",
            #     points=np.stack([agent_points_buffer, agents_pcd.points], 1),
            #     colors=colors,
            #     thickness=0.03,
            # )

            time.sleep(1/60)
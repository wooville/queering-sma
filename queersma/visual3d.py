from . import time
from . import viser
from . import trimesh
from . import numpy as np
from .helpers import *

class QSMAVisual3D():
    def __init__(self, sim):
        self.sim = sim

        server = viser.ViserServer()

        num_points = self.sim.params["agents_number"]

        # # Create colors based on height (z-coordinate).
        # z_min, z_max = spiral_positions[:, 2].min(), spiral_positions[:, 2].max()
        # normalized_z = (spiral_positions[:, 2] - z_min) / (z_max - z_min)

        # Color gradient from blue (bottom) to red (top).
        colors = np.zeros((num_points, 3), dtype=np.uint8)
        # colors[:, 0] = (normalized_z * 255).astype(np.uint8)  # Red channel.
        # colors[:, 2] = ((1 - normalized_z) * 255).astype(np.uint8)  # Blue channel.

        # Add the point cloud to the scene.
        agents_pcd = server.scene.add_point_cloud(
            name="/agents_cloud",
            position=(0,0,0),
            points=np.array([agent.position for agent in self.sim.agents]),
            colors=np.array([[agent.color[0], agent.color[1], agent.color[2]] for agent in self.sim.agents]),
            point_size=1,
            scale=1
        )

        # map_points = np.stack([range(0,self.sim.environment_map.shape[0]), range(0,self.sim.environment_map.shape[1]), range(0,self.sim.environment_map.shape[2])], 1)
        # print(np.array([[p, p, p] for p in self.sim.environment_map]).shape)
        # env_pcd = server.scene.add_point_cloud(
        #     name="/environment_cloud",
        #     points=map_points,
        #     colors=np.array([[self.sim.environment_map[p], self.sim.environment_map[p], self.sim.environment_map[p]] for p in map_points]),
        #     point_size=1,
        # )

        # Add a second point cloud - random noise points.
        # num_noise_points = 500
        # noise_positions = np.random.normal(0, 1, (num_noise_points, 3))
        # noise_colors = np.random.randint(0, 255, (num_noise_points, 3), dtype=np.uint8)

        # server.scene.add_point_cloud(
        #     name="/noise_cloud",
        #     points=noise_positions,
        #     colors=noise_colors,
        #     point_size=0.03,
        # )

        # server.scene.add_icosphere(
        #     name="/hello_sphere",
        #     radius=0.5,
        #     color=(255, 0, 0),  # Red
        #     position=(0.0, 0.0, 0.0),
        # )

        print("Open your browser to http://localhost:8080")
        print("Press Ctrl+C to exit")

        while True:
            self.sim.update(1/60)
            # agents_pcd.points = np.array([[agent.x, agent.y, agent.z] for agent in self.sim.agents])
            agents_pcd.points = np.array([agent.position for agent in self.sim.agents])
            # env_pcd.points = self.sim.environment_map
            # server.scene.add_image(
            #     "/environment_map",
            #     self.sim.environment_map,
            #     4.0,
            #     4.0,
            #     format="png",
            #     wxyz=(1.0, 0.0, 0.0, 0.0),
            #     position=agents_pcd.position,
            # )
            # server.scene.set_background_image(self.sim.environment_map)
            time.sleep(1/60)

        # instantiate QSMASimulation logic
        # self.sim = QSMASimulation(params=self.sim_params, signals=self.signals)
        # self.win = QSMAWindow(sim=self.sim, signals=self.signals, width=800, height=600, title="QSMA SIM", resizable=True)
        # set a framerate for the window
        # pyglet.clock.schedule_interval(self.update, 1/self.FRAME_RATE)
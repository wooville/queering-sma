This is (currently) a simple Python program that simulates the multi-agent model of slime mold initially designed by Jeff Jones.

An easy to follow, interactive explanation of the algorithm is available [here](https://denizbicer.com/202408-UnderstandingPhysarum.html).

The simulation is comprised of many individual "agents" that move around a 2D space. As the agents move, they leave a "trail" behind them; agents attempt to detect and follow the trails around them based on certain parameters. In this way, the simulation attempts to model the [cytoplasmic flow and networking behaviour of real-life slime mold](https://en.wikipedia.org/wiki/Physarum_polycephalum). Visualization of the agents and (especially) the trails they leave behind demonstrates varied and emergent pattern formation.

The simulation is managed and visualized in a window using the pyglet library. The imgui-bundle library is used to provide a simple user interface for adjusting the parameters of the simulation in real-time, dramatically altering agent behaviour.

<img width="640" height="638" alt="image" src="https://github.com/user-attachments/assets/a32ff0a2-8341-47fe-8294-c26d24ac15b2" />
<img width="638" height="642" alt="image" src="https://github.com/user-attachments/assets/d7e7dd14-0adf-416c-b12a-91272b976458" />

**Glossary**
Python: an accessible programming language that we used to create this app

**First time setup**
1. Download and install [Python 3.14](https://www.python.org/downloads/)
2. Clone (or download and unzip) this repository in an empty folder on your computer
3. Open a [terminal](https://www.technigo.io/explained/what-is-the-terminal) and navigate to the folder containing the repository using command
	```
	cd your\directory\here
 	```
4. Create a new virtual environment in this folder using the command
	```
	python -m venv .venv
 	```
5. Activate the virtual environment inside of the terminal using the command
	```
	Windows:		.venv\Scripts\activate.bat
	macOS\linux:	source .venv\Scripts\activate
	```
6. install dependencies into the virtual environment using the command
   ```
   pip install -r requirements.txt
   ```

**Running the program**
1. Activate the existing virtual environment using the command
   ```
   Windows:			.venv\Scripts\activate.bat
   macOS\linux:		source .venv\Scripts\activate
   ```
3. Run the program using the command
   ```
   python main.py
   ```

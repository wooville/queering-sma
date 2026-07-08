This is (currently) a simple Python program that simulates the multi-agent model of slime mold initially designed by Jeff Jones.

An easy to follow, interactive explanation of the algorithm is available [here](https://denizbicer.com/202408-UnderstandingPhysarum.html).

The simulation is comprised of many individual "agents" that move around a 2D space. As the agents move, they leave a "trail" behind them; agents attempt to detect and follow the trails around them based on an adjustable set of parameters. In this way, the simulation attempts to model the [cytoplasmic flow and networking behaviour of real-life slime mold](https://en.wikipedia.org/wiki/Physarum_polycephalum). Visualization of the agents and (especially) the trails they leave behind demonstrates varied and emergent pattern formation.

The simulation is managed and visualized in a window using the pyglet library. The imgui-bundle library is used to provide a simple user interface for adjusting the parameters of the simulation in real-time, dramatically altering agent behaviour.

<img width="640" height="640" alt="image" src="https://github.com/user-attachments/assets/a32ff0a2-8341-47fe-8294-c26d24ac15b2" />
<img width="640" height="640" alt="image" src="https://github.com/user-attachments/assets/d7e7dd14-0adf-416c-b12a-91272b976458" />

**Glossary**
- **Program**: a catch-all term very broadly referring to a list of instructions that we want a computer to perform; in our case, our main.py file is a Python script, which is a type of program
- **Programming language**: a strictly defined set of rules (and associated tools) that we can use to write our own programs
- **Python**: an accessible and flexible programming language; must download and install Python on your computer to run Python scripts!
	- **Dependency**: pre-existing Python code from the wider community that our code "depends" on to function; must be downloaded and installed into a Python environment
	- **Virtual environment**: an isolated Python environment on your computer to keep this project and its installed dependencies separate from any other Python projects; must be "activated" from the Terminal
- **Terminal**: a text-based ("command-line") interface packaged with your computer that allows you to handle technical tasks like file management and executing programs
	- **Commands**: the text that we input into the terminal to tell it what to do; if you cannot use Python related commands after installing Python, try closing the terminal and opening a new one

**First time setup**
1. Download and install [Python 3.14](https://www.python.org/downloads/)
2. Clone (or download and unzip) this repository in an empty folder on your computer
	- <img width="360" height="360" alt="image" src="https://github.com/user-attachments/assets/61626a13-304e-4255-b934-bbe0d1b25ba2" />
3. Open a [terminal](https://www.technigo.io/explained/what-is-the-terminal) on your computer and navigate to the folder containing the repository using command
	```
	cd your\directory\here
 	```
4. Use the command below to create a new virtual environment in the folder ".venv" (a subfolder in your terminal's current directory)
	```
	python -m venv .venv
 	```
5. Activate the virtual environment inside of the terminal using the command
	```
	Windows:		.venv\Scripts\activate.bat
	macOS\linux:	source .venv\Scripts\activate
	```
6. Install this project's dependencies into the virtual environment using the command
   ```
   pip install -r requirements.txt
   ```

**Running the program**
1. Activate the existing virtual environment using the command
   ```
   Windows:			.venv\Scripts\activate.bat
   macOS\linux:		source .venv\Scripts\activate
   ```
2. Run the program using the command
   ```
   python main.py
   ```

# ROS 2 Jazzy + Gazebo Harmonic + MuJoCo (CPU / macOS Intel Setup)

A Docker-based development environment for **ROS 2 Jazzy Jalisco**, **Gazebo Harmonic**, and **MuJoCo 3.x** optimized for macOS on Intel processors (`x86_64`).

This environment uses **noVNC + Xvfb** to render 3D graphics (RViz2, Gazebo, MuJoCo Viewer) via Mesa software rendering (`llvmpipe`), allowing you to view and interact with GUI applications directly from your web browser without depending on XQuartz or an Nvidia GPU.

## 🛠️ Prerequisites

* **Docker Desktop for Mac** (Intel `x86_64`)
* **Git**
* A modern web browser (Safari, Chrome, Firefox)

## 🚀 Quick Start

### 1. Clone the Repository
```
git clone <YOUR_REPOSITORY_URL>
cd ros2-jazzy-gpu
```

### 2. Build and Start the Container
```
docker compose build
docker compose up -d
```

### 3. Open the GUI in Your Browser
Navigate to the following URL in Safari or Chrome:
> [**http://localhost:8080/vnc.html**](http://localhost:8080/vnc.html)

Click the **Connect** button. You will see a virtual desktop running the Openbox window manager.

### 4. Attach to the Container Terminal
Open a terminal on your Mac and run:
```
docker compose exec ros2 bash
```

---

## 🛠 Container Installations & Setup Details

The container image includes all packages and dependencies required to support software rendering and simulation:

### Installed Packages Summary

1. **Base System & Tools:**
   * `ubuntu:24.04` (Noble Numbat)
   * `curl`, `gnupg2`, `lsb-release`, `build-essential`, `git`, `python3-pip`, `python3-venv`

2. **ROS 2 & Gazebo Stack:**
   * `ros-jazzy-desktop`
   * `ros-dev-tools`
   * `python3-colcon-common-extensions`
   * `gz-harmonic` (Gazebo Sim 8)
   * `ros-jazzy-ros-gz` (`ros_gz_bridge`)

3. **Virtual Framebuffer & Web GUI Stack:**
   * `xvfb` (X Virtual Framebuffer)
   * `openbox` (Lightweight window manager)
   * `x11vnc` (VNC server)
   * `novnc` & `python3-websockify` (Web browser access)

4. **Graphics Engine & Benchmarks:**
   * `mesa-utils`, `mesa-utils-bin`
   * `libgl1-mesa-dri`, `libglx-mesa0`, `libegl1`, `libgles2`
   * `x11-apps`
   * `glmark2` & `glmark2-es2`

5. **Physics & Simulation:**
   * `mujoco` Python bindings (v3.x)

---

## 🌐 Environment Variables Configuration

The following environment variables are set inside the container (and configured via `docker-compose.yml` / `entrypoint.sh`) to force software rendering and output GUI applications to the noVNC display server:

| Variable | Value | Description |
| :--- | :--- | :--- |
| `DISPLAY` | `:99` | Connects applications to the Xvfb virtual display buffer. |
| `LIBGL_ALWAYS_SOFTWARE` | `1` | Forces Mesa driver to use `llvmpipe` software rendering instead of hardware acceleration. |
| `QT_X11_NO_MITSHM` | `1` | Disables Shared Memory extension in Qt to prevent graphics glitches over VNC. |
| `MESA_GL_VERSION_OVERRIDE` | `4.5` | Exposes OpenGL 4.5 capabilities through software. |
| `GALLIUM_DRIVER` | `llvmpipe` | Instructs the Mesa Gallium driver to use CPU-based rasterization. |

---

## 🧪 Verifying the Installation

Inside the container terminal (`docker compose exec ros2 bash`), you can run the following sanity checks:

### 1. RViz2 Test
```
rviz2
```
* **Expected Result:** RViz2 opens in your browser window (`http://localhost:8080/vnc.html`).

### 2. Gazebo Harmonic Test
```
gz sim -v 4 empty.sdf
```
* **Expected Result:** Gazebo Sim opens a 3D grid world inside the browser window.

### 3. ROS 2 <-> Gazebo Bridge Test
```
ros2 run ros_gz_bridge parameter_bridge --help
```
* **Expected Result:** Displays topic bridging syntax options.

### 4. MuJoCo Python Verification
```
python3 -c "import mujoco; print(f'MuJoCo version: {mujoco.__version__}')"
```
* **Expected Result:** Prints `MuJoCo version: 3.16.0` (or current 3.x release).

### 5. OpenGL Benchmark
```
glmark2
```
* **Expected Result:** Runs 3D scene benchmarks in your browser using `llvmpipe`.

---

## 🧍 Running MuJoCo Simulations Without CPU Overload

To run a MuJoCo simulation without saturating your Mac's CPU cores, use a Python script with frame-rate control rather than the unthrottled `python3 -m mujoco.viewer`.

### Example Script (`test_view.py`)

Place `test_view.py` inside your `./ros2_ws` directory on your Mac:

```python
import os
import time
import mujoco
import mujoco.viewer

# Path to your downloaded XML model
model_path = os.path.expanduser('~/mujoco_models/humanoid.xml')

model = mujoco.MjModel.from_xml_path(model_path)
data = mujoco.MjData(model)

with mujoco.viewer.launch_passive(model, data) as viewer:
    while viewer.is_running():
        step_start = time.time()
        mujoco.mj_step(model, data)
        viewer.sync()
        
        # Throttle loop to match physics step (~60 FPS) to prevent CPU overuse
        time_until_next_step = model.opt.timestep - (time.time() - step_start)
        if time_until_next_step > 0:
            time.sleep(time_until_next_step)
```

### Execution Steps

1. Download the humanoid model inside the container:
   ```
   mkdir -p ~/mujoco_models && cd ~/mujoco_models
   curl -O https://raw.githubusercontent.com/google-deepmind/mujoco/main/model/humanoid/humanoid.xml
   ```

2. Run the script:
   ```
   cd /home/ros/ros2_ws
   python3 test_view.py
   ```

3. View the rendered model in your browser at `http://localhost:8080/vnc.html`.

---

## 📂 Project Structure

```
.
├── Dockerfile          # Ubuntu 24.04 base + ROS 2 Jazzy + Gazebo + Mesa/noVNC
├── docker-compose.yml  # Port mapping (8080), volume mounts, and environment flags
├── entrypoint.sh       # Launches Xvfb, Openbox, x11vnc, websockify, and ROS sources
└── ros2_ws/            # Local ROS 2 workspace mounted into /home/ros/ros2_ws
    ├── test_view.py    # MuJoCo CPU-throttled view script
    └── src/            # Put your ROS 2 packages here
```

---

## ⚡ Useful Commands

| Action | Command |
| :--- | :--- |
| **Start Environment** | `docker compose up -d` |
| **Stop Environment** | `docker compose down` |
| **Rebuild Container** | `docker compose build` |
| **Open Container Bash** | `docker compose exec ros2 bash` |
| **Kill Stuck Python/Sim Process** | `killall -9 python3` *(inside container)* |

---

## ⚙️ Architecture Notes (CPU vs. GPU)

* **Base Image:** `ubuntu:24.04` (Noble) running natively on `x86_64`.
* **Graphics Pipeline:** Software rendering powered by Mesa (`llvmpipe`), outputting OpenGL 4.5 through Xvfb virtual framebuffers.
* **Display Server:** `websockify` bridging `x11vnc` to `noVNC` on port `8080`.
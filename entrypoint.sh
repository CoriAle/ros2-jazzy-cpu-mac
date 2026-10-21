#!/bin/bash
set -e

# Configurar pantalla virtual
export DISPLAY=:99
Xvfb :99 -screen 0 1280x1024x24 &
sleep 1

# Iniciar gestor de ventanas
openbox &

# Iniciar servidor VNC y noVNC
x11vnc -display :99 -forever -shared -bg -nopw -quiet
websockify --web=/usr/share/novnc/ 8080 localhost:5900 &

# Entorno de ROS 2
source /opt/ros/jazzy/setup.bash
if [ -f /home/ros/ros2_ws/install/setup.bash ]; then
    source /home/ros/ros2_ws/install/setup.bash
fi

exec "$@"
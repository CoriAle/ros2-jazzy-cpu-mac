import os
import time
import mujoco
import mujoco.viewer

# Buscar el modelo descargado en el home del contenedor
model_path = os.path.expanduser('~/mujoco_models/humanoid.xml')

model = mujoco.MjModel.from_xml_path(model_path)
data = mujoco.MjData(model)

with mujoco.viewer.launch_passive(model, data) as viewer:
    while viewer.is_running():
        step_start = time.time()
        mujoco.mj_step(model, data)
        viewer.sync()
        
        # Sincroniza a ~60 FPS para no saturar la CPU
        time_until_next_step = model.opt.timestep - (time.time() - step_start)
        if time_until_next_step > 0:
            time.sleep(time_until_next_step)
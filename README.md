# MPC Fatigue

Folders description:

- Launch: It contains the launch files that loads the robotic arm system in Rviz.
- Plotter: It contains the results as images and video.
- Python: It contains the optimal control python script developed.
- Talkers: It contains python scripts that are used to plot the computed optimal solution in Rviz. 
- Urdf: It contains the urdf file that describes the robotic arm system.

## Windows via WSL2 (configured on this PC)

The `mpc-fatigue-ubuntu` WSL2 distribution, its ROS Noetic packages, the catkin
workspace, and the Python environment are stored in
`E:\Codex\mpc_fatigue_runtime\Ubuntu-20.04\ext4.vhdx`. The repository remains on
`E:\CartelleCondivise\GitHub_project\mpc_fatigue`. Run these commands in separate
PowerShell terminals:

```powershell
wsl -d mpc-fatigue-ubuntu -- bash -lc 'source /root/catkin_ws/install/setup.bash; roslaunch mpc_fatigue pilz_rviz_3DOF.launch'
```

```powershell
wsl -d mpc-fatigue-ubuntu -- bash /mnt/e/CartelleCondivise/GitHub_project/mpc_fatigue/scripts/run-python-wsl.sh /mnt/e/CartelleCondivise/GitHub_project/mpc_fatigue/python/Pilz_3_DOF/inverse_kinematics_pilz_3DOF.py
```

For the six-joint Pilz, launch `pilz_rviz_6DOF.launch` and run
`python/Pilz_6_DOF/inverse_kinematics_pilz_6DOF.py` with the same wrapper. For
the two-arm example, launch `2_pilz_rviz_6DOF.launch` and run
`python/2_pilz_6_DOF/inverse_kinematics.py`.

The Pilz force-optimization scripts for 3DOF and 6DOF run to completion, but
their later IPOPT solve reports local infeasibility with the current research
constraints. The 3DOF inverse-dynamics example reports the same solver status.
For the two-arm Box scripts, set `MPC_RUN_OCP=0` to plot an existing
`plotter/solution.csv` without rerunning the long optimization. Set
`MPC_PLOTTER_DIR` to an output directory on the E: backed WSL filesystem if
you want to keep generated CSVs and figures separate from tracked examples.
Both Box scripts were verified in this plot-only mode; a full Box OCP was
still iterating when a 120-second test limit was reached without an initial
guess. The first Box OCP converges when initialized from the tracked
`plotter/solution.csv` (1512 values). With the two-arm launch running, use:

```powershell
wsl -d mpc-fatigue-ubuntu -- env MPC_INITIAL_GUESS_CSV=/root/catkin_ws/src/mpc_fatigue/plotter/solution.csv MPC_PLOTTER_DIR=/root/mpc_box_output bash /root/catkin_ws/src/mpc_fatigue/scripts/run-python-wsl.sh /root/catkin_ws/src/mpc_fatigue/python/2_pilz_6_DOF/Box_Pilz_6DOF.py
```

The output directory is inside the E: backed WSL distribution. The second
Box variant accepts the same initial-guess option, but has different
constraints and is not yet confirmed to converge with this sample CSV.
Diagnostic continuation of its torque bounds converged with 7.5 Nm of
additional margin, then reported local infeasibility at 7 Nm. Those relaxed
solutions do not validate the original Box2 constraints.

Verified Box1 outputs (CSV, eight PNG figures, and solver log) are also saved
outside the repository at
`E:\Codex\mpc_fatigue_runtime\results\box1-verified-2026-11-07`.

After changing C++ or Python bridge code, rebuild inside WSL:

```bash
source /opt/ros/noetic/setup.bash
cd /root/catkin_ws
catkin_make install
```

The bridge uses the `mpc-py` environment under `/root/micromamba` inside the
E: backed distribution. To run the bridge and CSV warm-start tests:

```powershell
wsl -d mpc-fatigue-ubuntu -- bash /mnt/e/CartelleCondivise/GitHub_project/mpc_fatigue/scripts/run-python-wsl.sh -m unittest discover -s /mnt/e/CartelleCondivise/GitHub_project/mpc_fatigue/test -p test_*.py -v
```

## Centauro with the public model

The repository contains no Centauro URDF. An [external public model](https://github.com/ADVRHumanoids/iit-centauro-ros-pkg)
is available in this PC's E: backed WSL
distribution at `/root/external/iit-centauro-ros-pkg` (revision
`171690217a59a30e7c5bb5b30e19dc5f523a70d4`). The generated
`/root/external/centauro_14dof.urdf` fixes all non-arm joints and adds the
`mass1_ee` and `mass2_ee` frames expected by the scripts. Recreate it with:

```bash
python3 /root/catkin_ws/src/mpc_fatigue/scripts/prepare-centauro-model.py \
  /root/external/iit-centauro-ros-pkg/centauro_urdf/urdf/centauro.urdf \
  /root/external/centauro_14dof.urdf
```

The default box center in `MPC_parameters.py` is now `[0.8, 0, 0.8]` metres,
with the original 0.5 m width and 5 kg load. The study's previous center,
`[1.1, 0, 1.2]`, was outside the public model's reachable workspace. The new
pose reaches both hand targets within 1e-5 m while respecting joint limits.
Three complete MPC iterations converged with maximum constraint violation
about 0.000113, below the configured 0.001 tolerance. This is an adapted
simulation using the public model. Run it in two PowerShell terminals:

```powershell
wsl -d mpc-fatigue-ubuntu -- bash -lc 'source /root/catkin_ws/install/setup.bash; roslaunch mpc_fatigue centauro_public_model.launch'
```

```powershell
wsl -d mpc-fatigue-ubuntu -- bash /mnt/e/CartelleCondivise/GitHub_project/mpc_fatigue/scripts/run-python-wsl.sh /mnt/e/CartelleCondivise/GitHub_project/mpc_fatigue/python/Centauro_script/mpc_principal.py _max_iterations:=3
```

Omit `_max_iterations:=3` for continuous execution. Failed IK or OCP solves
raise an error before their results are published. To include the reachable
pose regression in the test command above, insert
`env MPC_CENTAURO_URDF=/root/external/centauro_14dof.urdf` after `--`.
The integration test otherwise skips when the external model is unavailable.
Reproducing the original study still requires its original model and frame
placement.

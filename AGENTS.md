# Repository Guidelines

## Project Structure & Module Organization

This repository is a ROS catkin package. C++ node code lives in `src/`, with public headers in `include/mpc_fatigue/`. `python/` contains optimal control experiments grouped by robot (`Centauro_script/`, `Pilz_3_DOF/`, `Pilz_6_DOF/`) and shared code in `python/Libraries/`. ROS publisher and playback scripts live in `talkers/`. Robot descriptions and visualization inputs are in `urdf/`, `meshes/`, and `launch/`; generated plots and example results are in `plotter/` and `Centauro_solutions/`. The optional Python binding is under `bindings/python/`.

## Build, Test, and Development Commands

Run these from a ROS environment with this package under a catkin workspace's `src/` directory:

```bash
cd ~/catkin_ws
catkin_make
source devel/setup.bash
rosrun mpc_fatigue talker
roslaunch mpc_fatigue pilz_rviz_6DOF.launch
```

`catkin_make` builds the C++ node; `catkin_make install` also installs the Python CasADi bridge. `source` exposes the package to ROS; the final two commands exercise the node and a Pilz RViz launch file. On this Windows PC, use the WSL2 environment and `scripts/run-python-wsl.sh` described in `README.md`. The legacy C++ bridge is optional and disabled by default.

## Coding Style & Naming Conventions

Use four-space indentation in C++ and Python, and follow the style of nearby files. Keep C++ headers under `include/mpc_fatigue/`; name new Python modules in `snake_case` and ROS launch files by robot and purpose (for example, `pilz_rviz_6DOF.launch`). No formatter or linter is configured, so keep changes focused and avoid reformatting unrelated experimental scripts.

## Testing Guidelines

Run the Python tests with the WSL command in `README.md`; they check the CasADi bridge against Pinocchio and validate CSV warm-start input. For other changes, build with `catkin_make install` and run the affected node or launch file. New reusable logic should get a focused test under `test/`; C++ tests can be registered with `catkin_add_gtest`.

## Commit & Pull Request Guidelines

Recent commits use short descriptive subjects rather than a strict prefix convention. Write a concise imperative subject naming the changed behavior. In pull requests, explain the robot or solver affected, required dependencies or configuration, and how you verified the change. Link a relevant issue when available; include RViz screenshots or plot comparisons for visual or trajectory changes.

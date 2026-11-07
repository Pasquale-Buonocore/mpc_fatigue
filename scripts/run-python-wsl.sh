#!/usr/bin/env bash
set -eo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
workspace="${MPC_CATKIN_WS:-/root/catkin_ws}"
conda_env="${MPC_CONDA_ENV:-/root/micromamba/envs/mpc-py}"

source "${workspace}/install/setup.bash"
set -u
export PYTHONPATH="${repo_dir}/python/Libraries:${repo_dir}/talkers/pilz_3_DOF:${repo_dir}/talkers/pilz_6_DOF:${repo_dir}/talkers/2_pilz_6_DOF:${repo_dir}/talkers/Centauros:${PYTHONPATH:-}"
export LD_LIBRARY_PATH="${conda_env}/lib:${LD_LIBRARY_PATH:-}"

exec "${conda_env}/bin/python" "$@"

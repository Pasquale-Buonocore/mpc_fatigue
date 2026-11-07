"""Smoke tests for the CasADi functions used by the Pilz solvers."""

from pathlib import Path
import unittest

import casadi as ca
import numpy as np
import pinocchio as pin

from mpc_fatigue import pynocchio_casadi as bridge


URDF = (Path(__file__).resolve().parents[1] / "urdf" / "pilz_robot_3DOF.urdf").read_text()


class CasadiBridgeTest(unittest.TestCase):
    def test_generated_functions_accept_three_joint_state(self):
        inverse_dynamics = ca.Function.deserialize(bridge.generate_inv_dyn(URDF))
        forward_kinematics = ca.Function.deserialize(
            bridge.generate_forward_kin(URDF, "prbt_flange")
        )
        jacobian = ca.Function.deserialize(
            bridge.generate_jacobian(URDF, "prbt_flange")
        )

        q = np.array([0.1, 0.2, -0.1])
        qdot = np.array([0.01, -0.02, 0.03])
        qddot = np.array([0.2, 0.1, -0.1])
        model = pin.buildModelFromXML(URDF)
        data = model.createData()
        frame_id = model.getFrameId("prbt_flange")

        torque = inverse_dynamics(q=q, qdot=qdot, qddot=qddot)["tau"]
        np.testing.assert_allclose(np.array(torque).ravel(), pin.rnea(model, data, q, qdot, qddot))
        pose = forward_kinematics(q=q)
        self.assertEqual(pose["ee_pos"].shape, (3, 1))
        self.assertEqual(pose["ee_rot"].shape, (3, 3))
        pin.framesForwardKinematics(model, data, q)
        np.testing.assert_allclose(np.array(pose["ee_pos"]).ravel(), data.oMf[frame_id].translation)
        np.testing.assert_allclose(np.array(pose["ee_rot"]), data.oMf[frame_id].rotation)
        pin.computeJointJacobians(model, data, q)
        expected = pin.getFrameJacobian(model, data, frame_id, pin.LOCAL_WORLD_ALIGNED)
        np.testing.assert_allclose(np.array(jacobian(q=q)["J"]), expected)


if __name__ == "__main__":
    unittest.main()

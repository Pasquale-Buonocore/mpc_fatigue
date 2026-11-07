"""Integration check for the reachable pose on an externally supplied URDF."""

import importlib
import os
from pathlib import Path
import unittest
from unittest.mock import patch

import numpy as np
import rospy


class CentauroPoseTest(unittest.TestCase):
    @unittest.skipUnless(os.environ.get('MPC_CENTAURO_URDF'),
                         'set MPC_CENTAURO_URDF to the reduced public model')
    def test_default_pose_is_reached_within_joint_limits(self):
        urdf = Path(os.environ['MPC_CENTAURO_URDF']).read_text()
        with patch.object(rospy, 'get_param', return_value=urdf):
            functions = importlib.import_module('Centauro_functions')
        from MPC_parameters import mpc

        with patch.object(functions, 'InvTalker'):
            q = functions.InvKin(mpc.box_initial_position, mpc.Lbox)
        values = np.asarray(q).reshape(-1)
        self.assertTrue(np.all(values >= functions.Centauro_features.joint_angle_lb - 1e-7))
        self.assertTrue(np.all(values <= functions.Centauro_features.joint_angle_ub + 1e-7))
        for fk, offset in ((functions.ForwKinLA, mpc.Lbox / 2),
                           (functions.ForwKinRA, -mpc.Lbox / 2)):
            target = mpc.box_initial_position + [0, offset, 0]
            np.testing.assert_allclose(np.asarray(fk(q, 'pos')).reshape(3), target, atol=1e-5)


if __name__ == '__main__':
    unittest.main()

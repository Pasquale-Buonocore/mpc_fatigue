"""Generate CasADi functions from URDF models through Pinocchio's Python API."""

import casadi as ca
import pinocchio as pin
import pinocchio.casadi as cpin


def _model(urdf_string):
    model = pin.buildModelFromXML(urdf_string)
    return cpin.Model(model)


def generate_inv_dyn(urdf_string):
    model = _model(urdf_string)
    data = model.createData()
    q = ca.SX.sym("q", model.nq)
    qdot = ca.SX.sym("qdot", model.nv)
    qddot = ca.SX.sym("qddot", model.nv)
    tau = cpin.rnea(model, data, q, qdot, qddot)
    return ca.Function(
        "inverse_dynamics", [q, qdot, qddot], [tau],
        ["q", "qdot", "qddot"], ["tau"],
    ).serialize()


def generate_forward_kin(urdf_string, body_name):
    model = _model(urdf_string)
    data = model.createData()
    q = ca.SX.sym("q", model.nq)
    frame_id = model.getFrameId(body_name)
    if frame_id == model.nframes:
        raise ValueError("Unknown URDF frame: {}".format(body_name))
    cpin.framesForwardKinematics(model, data, q)
    frame = data.oMf[frame_id]
    return ca.Function(
        "forward_kinematics", [q],
        [frame.translation, frame.rotation],
        ["q"], ["ee_pos", "ee_rot"],
    ).serialize()


def generate_jacobian(urdf_string, body_name):
    model = _model(urdf_string)
    data = model.createData()
    q = ca.SX.sym("q", model.nq)
    frame_id = model.getFrameId(body_name)
    if frame_id == model.nframes:
        raise ValueError("Unknown URDF frame: {}".format(body_name))
    cpin.computeJointJacobians(model, data, q)
    cpin.framesForwardKinematics(model, data, q)
    jacobian = cpin.getFrameJacobian(
        model, data, frame_id, pin.LOCAL_WORLD_ALIGNED,
    )
    return ca.Function(
        "jacobian", [q], [jacobian], ["q"], ["J"],
    ).serialize()

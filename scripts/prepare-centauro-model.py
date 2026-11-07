"""Adapt the public CENTAURO URDF to the 14 arm joints used by this project."""

import argparse
from pathlib import Path
import xml.etree.ElementTree as ET


ARM_JOINTS = {
    "j_arm{}_{}".format(arm, joint)
    for arm in (1, 2)
    for joint in range(1, 8)
}


def prepare(source, destination):
    tree = ET.parse(source)
    robot = tree.getroot()
    joints = robot.findall("joint")
    found = {joint.get("name") for joint in joints} & ARM_JOINTS
    if found != ARM_JOINTS:
        raise ValueError("CENTAURO URDF is missing arm joints: {}".format(sorted(ARM_JOINTS - found)))

    for joint in joints:
        if joint.get("name") not in ARM_JOINTS:
            joint.set("type", "fixed")

    for arm in (1, 2):
        frame = "mass{}_ee".format(arm)
        ET.SubElement(robot, "link", name=frame)
        joint = ET.SubElement(robot, "joint", name=frame + "_joint", type="fixed")
        ET.SubElement(joint, "parent", link="ball{}_tip".format(arm))
        ET.SubElement(joint, "child", link=frame)
        ET.SubElement(joint, "origin", xyz="0 0 0", rpy="0 0 0")

    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    tree.write(destination, encoding="utf-8", xml_declaration=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    prepare(args.source, args.destination)

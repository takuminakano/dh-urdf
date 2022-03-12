import argparse
from typing import Dict
import xml
# import lxml.etree
import xml.etree.ElementTree
from yaml import safe_load
import xml.dom.minidom


def add_box_visual(element, x_width, y_width, z_height, origin_by):
    visual_e = xml.etree.ElementTree.SubElement(element, "visual")
    geometry_e = xml.etree.ElementTree.SubElement(visual_e, "geometry")
    box_e = xml.etree.ElementTree.SubElement(geometry_e, "box")
    box_e.set("size", f"{x_width} {y_width} {z_height}")
    origin_e = xml.etree.ElementTree.SubElement(visual_e, "origin")
    if origin_by == "z":
        origin_e.set("xyz", f"0 0 {z_height/2}")
    elif origin_by == "x":
        origin_e.set("xyz", f"{x_width/2} 0 0")
    origin_e.set("rpy", "0 0 0")


def add_et_subtrees(parent_et, subtree_attributes: Dict):
    for subtree_attribute in subtree_attributes:
        subtree_e = xml.etree.ElementTree.SubElement(parent_et, subtree_attribute)
        for attr in subtree_attributes[subtree_attribute]:
            subtree_e.set(attr, subtree_attributes[subtree_attribute][attr])

def angle_to_radian(angle):
    return  3.1415926 * angle/180.0

def dh_to_urdf(dh):
    urdf_et = xml.etree.ElementTree.Element("robot")
    urdf_et.set("name", "robot")
    base_link = xml.etree.ElementTree.SubElement(urdf_et, "link")
    base_link.set("name", "L-0")
    add_box_visual(base_link, 1, 1, 3, "z")
    width = 1.0
    next_joint_origin = {
        "xpy": "0 0 3",
        "rpy": "0 0 0"
    }
    for link_index, dh_params in enumerate(dh):
        link_et = xml.etree.ElementTree.SubElement(urdf_et, "link")
        link_et.set("name", f"L-{link_index + 1}")
        if dh_params["d"] > dh_params["a"]:
            add_box_visual(link_et, width, width, dh_params["d"], "z")
        else:
            add_box_visual(link_et, dh_params["a"], width, width, "x")
        # if link_index == len(dh)-1:
        #     break
        joint_et = xml.etree.ElementTree.SubElement(urdf_et, "joint")
        joint_et.set("name", f"J-{link_index + 1}")
        joint_et.set("type", "revolute")
        add_et_subtrees(
            joint_et,
            {
                "parent": {"link": f"L-{link_index}"},
                "child": {"link": f"L-{link_index+1}"},
                "origin": next_joint_origin,
                "axis": {
                    "xyz": "0 0 1"
                },
                "limit": {
                    "effort": "1000",
                    "lower": "-2",
                    "upper": "2.0",
                    "velocity": "0.5"
                }
            }
        )
        next_joint_origin = {
            "xyz": f"{dh_params['a']} 0 {dh_params['d']}",
            "rpy": f"{angle_to_radian(dh_params['alpha'])} 0 0",
        }
    # return xml.etree.ElementTree.dump(urdf_et)
    # xml.etree.ElementTree.dump(urdf_et)
    return urdf_et


def dh_to_urdf_string(dh):
    return xml.etree.ElementTree.tostring(
        dh_to_urdf(dh)
    )


def xml_format(xml_content):
    dom = xml.dom.minidom.parseString(xml_content)
    return dom.toprettyxml()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--robot-yaml",
        help="path to robot.yaml"
    )
    parser.add_argument("--ouptut", "-o", required=True, help="output path(***.urdf)")
    args = parser.parse_args()
    with open(args.robot_yaml) as f:
        content = safe_load(f)
        et = dh_to_urdf(content)
        tree = xml.etree.ElementTree.ElementTree(et)
        formatted_xml = xml_format(xml.etree.ElementTree.tostring(et))
        with open(args.output) as o_f:
            o_f.write(formatted_xml)


if __name__ == "__main__":
    main()
    # with open("./robot.yaml") as f:
    #     content = safe_load(f)
    #     et = dh_to_urdf(content)
    #     tree = xml.etree.ElementTree.ElementTree(et)
    #     # tree.write("./robot2.urdf")
    #     # print(xml.etree.ElementTree.tostring(et))
    #     # print(lxml.etree.)
    #     # with open("./robot2.urdf", "w") as o:
    #     # tree = lxml.etree.ElementTree(lxml.etree.fromstring(xml.etree.ElementTree.tostring(et)))
    #     # print(tree)
    #     formatted_xml = xml_format(
    #         xml.etree.ElementTree.tostring(et)
    #     )
    #     print(formatted_xml)
    #     with open("./robot2.urdf", "w") as output_f:
    #         output_f.write(formatted_xml)
    #     # tree.write("./robot2.urdf", pretty_print = True)

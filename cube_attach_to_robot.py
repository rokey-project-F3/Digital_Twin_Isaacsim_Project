import omni.usd
from pxr import UsdGeom, Sdf, Gf, Usd, UsdPhysics
import omni.kit.app
from omni.isaac.dynamic_control import _dynamic_control
from sensor_msgs.msg import JointState

dc = _dynamic_control.acquire_dynamic_control_interface()
stage = omni.usd.get_context().get_stage()


CUBE_PATH = "/World/Cube"
BASE_LINK_PATH = "/World/Nova_Carter_ROS/chassis_link/base_link"

print("Cube:", CUBE_PATH)
print("Base:", BASE_LINK_PATH)

def get_world_position(prim_path):
    prim = stage.GetPrimAtPath(prim_path)
    if not prim.IsValid():
        return None
    xform = UsdGeom.Xformable(prim)
    mat = xform.ComputeLocalToWorldTransform(Usd.TimeCode.Default())
    return mat.ExtractTranslation()

attached = False

def on_update(dt):
    global attached

    robot_pos = get_world_position(BASE_LINK_PATH)
    cube_pos  = get_world_position(CUBE_PATH)


    if robot_pos is None or cube_pos is None:
        return

    dist = (cube_pos - robot_pos).GetLength()
    print("dist:", dist, attached)

    if (not attached) and dist < 1:
        print("📦 Attaching cube!")

        old = Sdf.Path(CUBE_PATH)
        new = Sdf.Path(BASE_LINK_PATH)

        print(old, new)

        # joint_props = _dynamic_control.D6JointProperties()
        # joint_props.name = "robot_cube_joint"
        # joint_props.body0 = old   # 부모 prim
        # joint_props.body1 = new  # 자식 prim

        
        joint_prim = UsdPhysics.FixedJoint.Define(stage, '/World/Cube/Joints')
        joint_prim.CreateBody0Rel().SetTargets([new])
        joint_prim.CreateBody1Rel().SetTargets([old])

        joint_prim.CreateLocalPos0Attr().Set(Gf.Vec3f(0.0, 0.0, 0.6))

        attached = True



subscription = omni.kit.app.get_app().get_update_event_stream().create_subscription_to_pop(on_update)
print("✔ Distance-based attach system activated!")
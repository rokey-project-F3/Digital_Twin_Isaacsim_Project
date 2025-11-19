import omni.usd
from pxr import UsdGeom, Sdf, Gf, Usd
import omni.kit.app

stage = omni.usd.get_context().get_stage()

CUBE_PATH = "/World/PROJECT_1/Cube"
BASE_LINK_PATH = "/World/PROJECT_1/Nova_Carter_ROS/chassis_link"

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
    # print("dist:", dist)

    if (not attached) and dist < 0.3:
        print("📦 Attaching cube!")

        old = Sdf.Path(CUBE_PATH)
        new = Sdf.Path(BASE_LINK_PATH).AppendChild("Cube")

        ok = stage.MovePrim(old, new)

        if ok:
            print("✅ Attached!")
            attached = True
        else:
            print("❌ MovePrim failed")


subscription = omni.kit.app.get_app().get_update_event_stream().create_subscription_to_pop(on_update)
print("✔ Distance-based attach system activated!")
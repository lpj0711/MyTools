from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Core.IFSelect import IFSelect_RetDone
from OCC.Display.SimpleGui import init_display
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopoDS import topods
from OCC.Core.TopAbs import TopAbs_EDGE, TopAbs_FACE, TopAbs_WIRE, TopAbs_VERTEX
from OCC.Core.BRep import BRep_Tool
from OCC.Core.gp import gp_Pnt
from OCC.Core.BRepExtrema import BRepExtrema_DistShapeShape
from OCC.Core.Quantity import Quantity_Color, Quantity_NOC_GRAY, Quantity_NOC_RED, Quantity_NOC_YELLOW, Quantity_TOC_RGB
from OCC.Core.Prs3d import Prs3d_PointAspect
from OCC.Core.Aspect import Aspect_TOM_BALL
from OCC.Core.AIS import AIS_Point
from OCC.Core.Geom import Geom_CartesianPoint

def read_step_file(filename):
    """读取STEP文件并返回形状。"""
    step_reader = STEPControl_Reader()
    status = step_reader.ReadFile(filename)
    if status == IFSelect_RetDone:
        step_reader.TransferRoots()
        shape = step_reader.OneShape()
        return shape
    else:
        print("错误：无法读取文件。")
        return None

def get_intersection_points(shape):
    """查找形状中所有边的交点。"""
    edges = []
    exp = TopExp_Explorer(shape, TopAbs_EDGE)
    while exp.More():
        edges.append(topods.Edge(exp.Current()))
        exp.Next()

    intersection_points = []
    for i in range(len(edges)):
        for j in range(i + 1, len(edges)):
            edge1 = edges[i]
            edge2 = edges[j]
            dist = BRepExtrema_DistShapeShape(edge1, edge2)
            if dist.IsDone() and dist.Value() < 1e-7:
                p1 = dist.PointOnShape1(1)
                p2 = dist.PointOnShape2(1)
                if p1.IsEqual(p2, 1e-6):
                    is_duplicate = False
                    for p in intersection_points:
                        if p.IsEqual(p1, 1e-6):
                            is_duplicate = True
                            break
                    if not is_duplicate:
                        intersection_points.append(p1)
    return intersection_points

def get_hole_elements(shape):
    """查找形状中所有孔洞的边和顶点。"""
    hole_edges = set()
    hole_vertices = set()
    
    face_explorer = TopExp_Explorer(shape, TopAbs_FACE)
    while face_explorer.More():
        face = topods.Face(face_explorer.Current())
        wire_explorer = TopExp_Explorer(face, TopAbs_WIRE)
        is_outer_wire = True
        while wire_explorer.More():
            if not is_outer_wire:
                # 这个线圈定义了一个孔洞
                hole_wire = topods.Wire(wire_explorer.Current())
                
                # 从孔洞线圈中获取边
                edge_explorer = TopExp_Explorer(hole_wire, TopAbs_EDGE)
                while edge_explorer.More():
                    hole_edges.add(edge_explorer.Current())
                    edge_explorer.Next()
                
                # 从孔洞线圈中获取顶点
                vertex_explorer = TopExp_Explorer(hole_wire, TopAbs_VERTEX)
                while vertex_explorer.More():
                    hole_vertices.add(vertex_explorer.Current())
                    vertex_explorer.Next()

            is_outer_wire = False
            wire_explorer.Next()
        face_explorer.Next()
        
    return hole_edges, hole_vertices

if __name__ == "__main__":
    # 初始化显示
    display, start_display, add_menu, add_function_to_menu = init_display()
    
    # 读取STEP文件
    file_path = r"D:\DataSet\step_temp\00000001.stp"
    my_shape = read_step_file(file_path)

    if my_shape:
        # 1. 获取所有几何数据
        hole_edges, hole_vertices = get_hole_elements(my_shape)
        print(f"找到 {len(hole_edges)} 条孔洞边。")
        print(f"找到 {len(hole_vertices)} 个孔洞顶点。")
        
        intersection_points = get_intersection_points(my_shape)
        print(f"找到 {len(intersection_points)} 个交点。")

        # 2. 首先显示所有边
        edge_explorer = TopExp_Explorer(my_shape, TopAbs_EDGE)
        while edge_explorer.More():
            edge = edge_explorer.Current()
            if edge in hole_edges:
                display.DisplayShape(edge, update=False, color=Quantity_NOC_YELLOW)
            else:
                display.DisplayShape(edge, update=False, color=Quantity_NOC_GRAY)
            edge_explorer.Next()

        # 3. 创建点样式和颜色
        red_color = Quantity_Color(1.0, 0.0, 0.0, Quantity_TOC_RGB)
        yellow_color = Quantity_Color(1.0, 1.0, 0.0, Quantity_TOC_RGB)
        red_point_aspect = Prs3d_PointAspect(Aspect_TOM_BALL, red_color, 5.0)
        yellow_point_aspect = Prs3d_PointAspect(Aspect_TOM_BALL, yellow_color, 5.0)

        # 4. 为快速查找创建孔洞顶点坐标集
        hole_vertex_coords = set()
        for vtx in hole_vertices:
            p_vtx = BRep_Tool.Pnt(vtx)
            key = (round(p_vtx.X(), 5), round(p_vtx.Y(), 5), round(p_vtx.Z(), 5))
            hole_vertex_coords.add(key)

        # 5. 显示所有孔洞顶点 (黄色)
        for vtx in hole_vertices:
            p_vtx = BRep_Tool.Pnt(vtx)
            geom_point = Geom_CartesianPoint(p_vtx)
            ais_point = AIS_Point(geom_point)
            ais_point.SetColor(yellow_color)
            ais_point.SetMarker(Aspect_TOM_BALL)
            ais_point.Attributes().SetPointAspect(yellow_point_aspect)
            display.Context.Display(ais_point, True)

        # 6. 显示不属于孔洞的交点 (红色)
        for pnt in intersection_points:
            key = (round(pnt.X(), 5), round(pnt.Y(), 5), round(pnt.Z(), 5))
            if key not in hole_vertex_coords:
                geom_point = Geom_CartesianPoint(pnt)
                ais_point = AIS_Point(geom_point)
                ais_point.SetColor(red_color)
                ais_point.SetMarker(Aspect_TOM_BALL)
                ais_point.Attributes().SetPointAspect(red_point_aspect)
                display.Context.Display(ais_point, True)

        # 适应视图并开始显示
        display.FitAll()
        start_display()
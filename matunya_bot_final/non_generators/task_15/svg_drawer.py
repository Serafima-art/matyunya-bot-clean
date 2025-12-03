import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

Point = Tuple[float, float]


@dataclass
class SVGTemplate:
    width: int
    height: int
    points: Dict[str, Point]
    lines: Dict[str, Tuple[str, str]]
    static_decorations: List[dict] = field(default_factory=list)

    @property
    def view_box(self) -> str:
        return f"0 0 {self.width} {self.height}"


class SVGDrawer:
    def __init__(self) -> None:
        self.templates: Dict[str, SVGTemplate] = {}
        self._build_templates()

    def _build_templates(self) -> None:
        w, h = 260, 200
        templates: Dict[str, SVGTemplate] = {}

        # T1 — Прямоугольный треугольник (угол C = 90°)
        points_T1 = {"A": (40, 160), "C": (160, 160), "B": (160, 40)}
        lines_T1 = {"AB": ("A", "B"), "AC": ("A", "C"), "BC": ("B", "C")}
        templates["T1"] = SVGTemplate(w, h, points_T1, lines_T1)

        # T1a — T1 + медиана CM
        points_T1a = dict(points_T1)
        points_T1a["M"] = (
            (points_T1["A"][0] + points_T1["B"][0]) / 2,
            (points_T1["A"][1] + points_T1["B"][1]) / 2,
        )
        lines_T1a = dict(lines_T1)
        lines_T1a.update({"CM": ("C", "M"), "AM": ("A", "M"), "MB": ("M", "B")})
        templates["T1a"] = SVGTemplate(w, h, points_T1a, lines_T1a)

        # T2 — Равнобедренный треугольник (основание AC, угол B тупой)
        points_T2 = {"A": (40, 170), "C": (220, 170), "B": (120, 110)}
        lines_T2 = {"AB": ("A", "B"), "BC": ("B", "C"), "AC": ("A", "C")}
        deco_T2 = [
            {"type": "equality_tick", "on_segment": "AB", "style": "single_dash"},
            {"type": "equality_tick", "on_segment": "BC", "style": "single_dash"},
        ]
        templates["T2"] = SVGTemplate(w, h, points_T2, lines_T2, deco_T2)

        # T3 — Остроугольный треугольник
        points_T3 = {"A": (40, 170), "C": (210, 150), "B": (150, 50)}
        lines_T3 = {"AB": ("A", "B"), "BC": ("B", "C"), "AC": ("A", "C")}
        templates["T3"] = SVGTemplate(w, h, points_T3, lines_T3)

        # T4 — T3 + точка D на AC
        points_T4 = dict(points_T3)
        points_T4["D"] = (
            points_T4["A"][0] + 0.4 * (points_T4["C"][0] - points_T4["A"][0]),
            points_T4["A"][1] + 0.4 * (points_T4["C"][1] - points_T4["A"][1]),
        )
        lines_T4 = dict(lines_T3)
        lines_T4.update({"BD": ("B", "D"), "AD": ("A", "D"), "DC": ("D", "C")})
        templates["T4"] = SVGTemplate(w, h, points_T4, lines_T4)

        # T5 — T3 + линия MN || AC
        points_T5 = dict(points_T3)
        points_T5["M"] = (
            points_T5["A"][0] + 0.5 * (points_T5["B"][0] - points_T5["A"][0]),
            points_T5["A"][1] + 0.5 * (points_T5["B"][1] - points_T5["A"][1]),
        )
        points_T5["N"] = (
            points_T5["C"][0] + 0.5 * (points_T5["B"][0] - points_T5["C"][0]),
            points_T5["C"][1] + 0.5 * (points_T5["B"][1] - points_T5["C"][1]),
        )
        lines_T5 = dict(lines_T3)
        lines_T5.update({"MN": ("M", "N"), "AM": ("A", "M"), "NC": ("N", "C")})
        templates["T5"] = SVGTemplate(w, h, points_T5, lines_T5)

        # T6 — T3 + средняя линия MN
        points_T6 = dict(points_T3)
        points_T6["M"] = (
            (points_T6["A"][0] + points_T6["B"][0]) / 2,
            (points_T6["A"][1] + points_T6["B"][1]) / 2,
        )
        points_T6["N"] = (
            (points_T6["B"][0] + points_T6["C"][0]) / 2,
            (points_T6["B"][1] + points_T6["C"][1]) / 2,
        )
        lines_T6 = dict(lines_T3)
        lines_T6.update(
            {"MN": ("M", "N"), "AM": ("A", "M"), "MB": ("M", "B"), "BN": ("B", "N"), "NC": ("N", "C")}
        )
        templates["T6"] = SVGTemplate(w, h, points_T6, lines_T6)

        # Базовая геометрия равностороннего треугольника для T7-вариантов
        points_T7 = {"A": (50, 170), "C": (210, 170), "B": (130, 30.7), "H": (130, 170)}
        lines_T7 = {"AB": ("A", "B"), "BC": ("B", "C"), "AC": ("A", "C"), "BH": ("B", "H")}

        # T7_height — высота с прямым углом у основания
        deco_T7_height = [
            {"type": "right_angle_square", "at_vertex": "H", "neighbors": ["A", "C"]},
        ]
        templates["T7_height"] = SVGTemplate(w, h, points_T7, lines_T7, deco_T7_height)

        # T7_median — штрихи на AH и HC
        deco_T7_median = [
            {"type": "equality_tick", "on_segment": "AH", "style": "single_dash"},
            {"type": "equality_tick", "on_segment": "HC", "style": "single_dash"},
        ]
        templates["T7_median"] = SVGTemplate(w, h, points_T7, lines_T7, deco_T7_median)

        # T7_bisector — две одинаковые дуги у вершины B
        deco_T7_bisector = [
            {"type": "angle_arc", "at_vertex": "B", "style": "double"},
        ]
        templates["T7_bisector"] = SVGTemplate(w, h, points_T7, lines_T7, deco_T7_bisector)

        # T8 — T3 + биссектриса AD
        points_T8 = dict(points_T3)
        points_T8["D"] = (
            (points_T8["B"][0] + points_T8["C"][0]) / 2,
            (points_T8["B"][1] + points_T8["C"][1]) / 2,
        )
        lines_T8 = dict(lines_T3)
        lines_T8["AD"] = ("A", "D")
        deco_T8 = [
            {"type": "angle_arc", "at_vertex": "A", "style": "double"},
        ]
        templates["T8"] = SVGTemplate(w, h, points_T8, lines_T8, deco_T8)

        # T9 — T3 + внешний угол у C
        points_T9 = {"A": (40, 170), "C": (200, 170), "B": (240, 80)}
        points_T9["E"] = (280, 170)
        lines_T9 = {"AB": ("A", "B"), "BC": ("B", "C"), "AC": ("A", "C"), "CE": ("C", "E")}
        templates["T9"] = SVGTemplate(w, h, points_T9, lines_T9)

        self.templates = templates

    def draw(self, drawing_info: dict) -> str:
        template_id = drawing_info.get("template_id")
        if not template_id:
            raise ValueError("drawing_info must include a template_id")

        template = self.templates.get(template_id)
        if template is None:
            raise ValueError(f"Unknown template_id: {template_id}")

        elements: List[str] = []
        self._draw_template_lines(elements, template, drawing_info)
        self._draw_labels(elements, template, drawing_info)
        decorations = list(template.static_decorations)
        decorations.extend(drawing_info.get("decorations", []))
        self._draw_decorations(elements, template, decorations)
        self._draw_highlights(elements, template, drawing_info)

        svg_body = "\n".join(elements)
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{template.width}" height="{template.height}" '
            f'viewBox="{template.view_box}">\n{svg_body}\n</svg>'
        )

    def _draw_template_lines(
        self,
        elements: List[str],
        template: SVGTemplate,
        drawing_info: dict,
    ) -> None:
        # Добавляем белый фон
        elements.append(f'<rect width="100%" height="100%" fill="white" />')

        for _, (p1_name, p2_name) in template.lines.items():
            p1 = template.points[p1_name]
            p2 = template.points[p2_name]

            # Атрибуты для ВСЕХ линий - единый стиль
            attrs = {
                "x1": str(p1[0]),
                "y1": str(p1[1]),
                "x2": str(p2[0]),
                "y2": str(p2[1]),
                "stroke": "#0456a2",       # Стандартный синий
                "stroke-width": "2",
                "stroke-linecap": "round",  # Сглаживание концов
                "stroke-linejoin": "round", # Сглаживание соединений
                "fill": "none",
            }

            line_str = " ".join(f'{k}="{v}"' for k, v in attrs.items())
            elements.append(f"<line {line_str} />")

    def _find_vertex_neighbors(self, template: SVGTemplate, vertex: str) -> List[str]:
        neighbors: List[str] = []
        for _, (p1, p2) in template.lines.items():
            if p1 == vertex and p2 not in neighbors:
                neighbors.append(p2)
            elif p2 == vertex and p1 not in neighbors:
                neighbors.append(p1)
        return neighbors

    def _get_segment_points(
        self, template: SVGTemplate, segment_name: str
    ) -> Optional[Tuple[Point, Point]]:
        if segment_name in template.lines:
            a, b = template.lines[segment_name]
            return template.points.get(a), template.points.get(b)
        if len(segment_name) == 2:
            a, b = segment_name[0], segment_name[1]
            if a in template.points and b in template.points:
                return template.points[a], template.points[b]
        return None

    def _draw_right_angle_square(
        self,
        elements: List[str],
        template: SVGTemplate,
        vertex_name: str,
        neighbors: Optional[List[str]] = None,
        size: float = 14.0,
    ) -> None:
        neighbor_list = neighbors or self._find_vertex_neighbors(template, vertex_name)
        if len(neighbor_list) < 2:
            return

        p0 = template.points.get(vertex_name)
        p1 = template.points.get(neighbor_list[0])
        p2 = template.points.get(neighbor_list[1])
        if not p0 or not p1 or not p2:
            return

        v1 = (p1[0] - p0[0], p1[1] - p0[1])
        v2 = (p2[0] - p0[0], p2[1] - p0[1])

        def _norm(v: Tuple[float, float]) -> float:
            return math.hypot(v[0], v[1])

        def _unit(v: Tuple[float, float]) -> Tuple[float, float]:
            n = _norm(v)
            if n == 0:
                return (0.0, 0.0)
            return (v[0] / n, v[1] / n)

        u1 = _unit(v1)
        u2 = _unit(v2)

        p_a = (p0[0] + u1[0] * size, p0[1] + u1[1] * size)
        p_b = (p_a[0] + u2[0] * size, p_a[1] + u2[1] * size)
        p_c = (p0[0] + u2[0] * size, p0[1] + u2[1] * size)

        path_d = (
            f"M{p_a[0]:.1f},{p_a[1]:.1f} "
            f"L{p_b[0]:.1f},{p_b[1]:.1f} "
            f"L{p_c[0]:.1f},{p_c[1]:.1f} Z"
        )
        elements.append(
            f'<path d="{path_d}" fill="none" stroke="#0456a2" stroke-width="2" stroke-linejoin="round" />'
        )

    def _draw_angle_arc(
        self,
        elements: List[str],
        template: SVGTemplate,
        vertex_name: str,
        style: str = "single",
        radius: float = 16.0,
    ) -> None:
        base_vertex = vertex_name
        if vertex_name.endswith("_external"):
            base_vertex = vertex_name.split("_")[0]

        neighbors = self._find_vertex_neighbors(template, base_vertex)
        if len(neighbors) < 2:
            return

        # Для внешних углов стараемся выбрать внешнюю точку, если есть
        if vertex_name.endswith("_external"):
            external_neighbor = None
            for n in neighbors:
                if n.lower().startswith("e"):
                    external_neighbor = n
                    break
            if external_neighbor and len(neighbors) > 1:
                others = [n for n in neighbors if n != external_neighbor]
                neighbors = [external_neighbor, others[0]]

        center = template.points.get(base_vertex)
        p1 = template.points.get(neighbors[0])
        p2 = template.points.get(neighbors[1])
        if not center or not p1 or not p2:
            return

        v1 = (p1[0] - center[0], p1[1] - center[1])
        v2 = (p2[0] - center[0], p2[1] - center[1])

        a1 = math.atan2(v1[1], v1[0])
        a2 = math.atan2(v2[1], v2[0])

        delta = (a2 - a1) % (2 * math.pi)
        if delta > math.pi:
            delta -= 2 * math.pi

        large_arc = 1 if abs(delta) > math.pi else 0
        sweep = 1 if delta >= 0 else 0

        def _arc_path(r: float) -> str:
            start = (center[0] + r * math.cos(a1), center[1] + r * math.sin(a1))
            end = (center[0] + r * math.cos(a2), center[1] + r * math.sin(a2))
            return (
                f"M{start[0]:.1f},{start[1]:.1f} "
                f"A{r},{r} 0 {large_arc} {sweep} {end[0]:.1f},{end[1]:.1f}"
            )

        arcs: List[Tuple[str, Dict[str, str]]] = []
        base_attrs = {
            "fill": "none",
            "stroke": "#0456a2",
            "stroke-width": "2",
        }

        if style == "double":
            arcs.append((_arc_path(radius), base_attrs))
            arcs.append((_arc_path(max(radius - 4, 4)), base_attrs))
        else:
            attrs = dict(base_attrs)
            if style == "bold_fill":
                attrs["stroke-width"] = "3.5"
            arcs.append((_arc_path(radius), attrs))

        for d, attrs in arcs:
            attr_str = " ".join(f'{k}="{v}"' for k, v in attrs.items())
            elements.append(f'<path d="{d}" {attr_str} />')

    def _draw_equality_tick(
        self,
        elements: List[str],
        template: SVGTemplate,
        segment_name: str,
        style: str = "single_dash",
    ) -> None:
        pts = self._get_segment_points(template, segment_name)
        if not pts or not pts[0] or not pts[1]:
            return

        p1, p2 = pts
        v = (p2[0] - p1[0], p2[1] - p1[1])
        length = math.hypot(v[0], v[1])
        if length == 0:
            return
        u = (v[0] / length, v[1] / length)
        n = (-u[1], u[0])

        count = 2 if style == "double_dash" else 1
        offset_along = 0 if count == 1 else 6
        tick_len = 8.0

        centers = []
        base_center = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
        if count == 1:
            centers.append(base_center)
        else:
            centers.append(
                (base_center[0] + u[0] * offset_along, base_center[1] + u[1] * offset_along)
            )
            centers.append(
                (base_center[0] - u[0] * offset_along, base_center[1] - u[1] * offset_along)
            )

        for cx, cy in centers:
            p_start = (cx - n[0] * tick_len / 2, cy - n[1] * tick_len / 2)
            p_end = (cx + n[0] * tick_len / 2, cy + n[1] * tick_len / 2)
            elements.append(
                f'<line x1="{p_start[0]:.1f}" y1="{p_start[1]:.1f}" '
                f'x2="{p_end[0]:.1f}" y2="{p_end[1]:.1f}" '
                f'stroke="#0456a2" stroke-width="2" stroke-linecap="round" />'
            )

    def _draw_labels(
        self,
        elements: List[str],
        template: SVGTemplate,
        drawing_info: dict,
    ) -> None:
        pass

    def _draw_decorations(
        self,
        elements: List[str],
        template: SVGTemplate,
        decorations: List[dict],
    ) -> None:
        for deco in decorations:
            if not isinstance(deco, dict):
                continue
            deco_type = deco.get("type")
            if deco_type == "right_angle_square":
                vertex = deco.get("at_vertex")
                neighbors = deco.get("neighbors")
                if vertex:
                    self._draw_right_angle_square(elements, template, vertex, neighbors=neighbors)
            elif deco_type == "angle_arc":
                vertex = deco.get("at_vertex") or deco.get("angle_name")
                style = deco.get("style", "single")
                if vertex:
                    self._draw_angle_arc(elements, template, vertex, style=style)
            elif deco_type == "equality_tick":
                segment = deco.get("on_segment")
                style = deco.get("style", "single_dash")
                if segment:
                    self._draw_equality_tick(elements, template, segment, style=style)

    def _draw_highlights(
        self,
        elements: List[str],
        template: SVGTemplate,
        drawing_info: dict,
    ) -> None:
        pass


if __name__ == "__main__":
    drawer = SVGDrawer()
    sample_drawing_info = {
        "template_id": "T1",
        "labels": [{"type": "side", "name": "AC", "text": "15"}],
        "decorations": [
            {"type": "right_angle_square", "at_vertex": "C"},
            {"type": "angle_arc", "at_vertex": "A", "style": "single"},
            {"type": "angle_arc", "at_vertex": "B", "style": "double"},
        ],
        "highlights": [{"type": "line", "name": "AB", "style": "bold_stroke"}],
    }
    print(drawer.draw(sample_drawing_info))

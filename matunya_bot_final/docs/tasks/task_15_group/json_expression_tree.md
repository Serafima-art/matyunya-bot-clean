Финальный Эталон Структуры JSON (Версия 3.0, Полная)

{
  "id": 0,
  "pattern": "pattern_name",
  "text": "Полный текст задачи.",
  "answer": null,
  "image_svg": "",

  "variables": {
    "given": {
      "triangle_name": "",
      "triangle_type": "general | right | isosceles | equilateral",

      "sides": {},
      "angles": {},
      "trig": {},

      "elements": {},
      "points": {},
      "relations": {}
    },

    "to_find": {
      "type": "side | angle | area",
      "name": ""
    },

    "humanizer_data": {
      "side_roles": {},
      "angle_names": {},
      "element_names": {}
    },

    "drawing_info": {
      "template_id": "T1",

      "labels": [
        /*
        Пример элемента:
        {"type": "vertex", "name": "A", "text": "A"}
        */
      ],

      "decorations": [
        /*
        Пример:
        {"type": "right_angle_square", "at_vertex": "C"}
        */
      ],

      "highlights": []
    }
  }
}



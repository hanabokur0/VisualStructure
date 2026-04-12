# examples/ui_example.py

from visual_structure.analyzer import VisualStructureAnalyzer


def build_sample_ui_elements():
    """
    Simulated UI elements (no CV required).
    """

    return [
        {
            "id": "title",
            "type": "text",
            "x": 0.5,
            "y": 0.1,
            "w": 0.6,
            "h": 0.1,
            "salience": 0.7,
            "label": "Product Title"
        },
        {
            "id": "price",
            "type": "text",
            "x": 0.5,
            "y": 0.25,
            "w": 0.3,
            "h": 0.1,
            "salience": 0.6,
            "label": "¥12,800"
        },
        {
            "id": "stock",
            "type": "text",
            "x": 0.5,
            "y": 0.4,
            "w": 0.4,
            "h": 0.1,
            "salience": 0.3,
            "label": "Out of stock"
        },
        {
            "id": "buy_button",
            "type": "button",
            "x": 0.5,
            "y": 0.7,
            "w": 0.4,
            "h": 0.15,
            "salience": 1.0,
            "label": "Buy Now"
        }
    ]


def build_sample_relations():
    return [
        {"from": "title", "to": "price", "relation_type": "hierarchical"},
        {"from": "price", "to": "stock", "relation_type": "flow"},
        {"from": "stock", "to": "buy_button", "relation_type": "flow"},
    ]


def main():
    elements = build_sample_ui_elements()
    relations = build_sample_relations()

    analyzer = VisualStructureAnalyzer()
    result = analyzer.analyze(elements, relations)

    print("=== VisualStructure Output ===")
    print(result)


if __name__ == "__main__":
    main()

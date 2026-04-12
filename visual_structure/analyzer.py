# visual_structure/analyzer.py

from typing import Dict, Any
from .metrics import compute_metrics
from .schema import VisualStructureOutput


class VisualStructureAnalyzer:
    """
    Core analyzer for extracting visual structure.

    Responsibilities:
    - receive pre-processed visual elements
    - compute visual metrics
    - return structured output

    This layer does NOT:
    - perform OCR
    - generate captions
    - interpret meaning
    """

    def __init__(self):
        pass

    def analyze(self, elements: list, relations: list = None) -> Dict[str, Any]:
        """
        Main entry point.

        Args:
            elements (list): detected visual elements
            relations (list): optional relationships between elements

        Returns:
            dict: structured visual representation
        """

        if relations is None:
            relations = []

        # Compute metrics
        metrics = compute_metrics(elements, relations)

        # Build output structure
        output = VisualStructureOutput(
            elements=elements,
            relations=relations,
            visual_metrics=metrics
        )

        return output.to_dict()

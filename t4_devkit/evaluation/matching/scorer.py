from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, TypeVar

import numpy as np

from t4_devkit.dataclass import Box3D

if TYPE_CHECKING:
    from t4_devkit.dataclass import BoxType

__all__ = [
    "MatchingScorerLike",
    "MatchingScorerImpl",
    "CenterDistance",
    "PlaneDistance",
    "Iou2D",
    "Iou3D",
]


class MatchingScorerImpl(ABC):
    """Abstract base class of the function of matching scorer."""

    def __call__(self, box1: BoxType, box2: BoxType) -> float:
        self._validate(box1, box2)
        return self._calculate_score(box1, box2)

    def _validate(self, box1: BoxType, box2: BoxType) -> None:
        """Validate the input two boxes.

        Args:
            box1 (BoxType): A box.
            box2 (BoxType): A box.

        Raises:
            TypeError: Expecting two boxes have the same type.
        """
        if not isinstance(box1, type(box2)):
            raise TypeError(
                f"Both boxes must be the same type, but got {type(box1)} and {type(box2)}."
            )

    def is_better_than(self, score: float, threshold: float) -> bool:
        """Check if the matching score of the input boxes satisfies the threshold.

        Args:
            score (float): Matching score.
            threshold (float): Threshold value of the matching score.

        Returns:
            Returns `True` the calculated matching score is better than the threshold.
        """
        return score <= threshold if self.smaller_is_better() else threshold <= score

    @abstractmethod
    @classmethod
    def smaller_is_better(cls) -> bool:
        """Indicate whether the smaller matching score is better.

        Returns:
            Returns `True` if the smaller score is better.
        """
        pass

    @abstractmethod
    def _calculate_score(self, box1: BoxType, box2: BoxType) -> float:
        """Calculate the matching score of the input two boxes.

        Args:
            box1 (BoxType): A box.
            box2 (BoxType): A box.

        Returns:
            Calculated matching score.
        """
        pass


class CenterDistance(MatchingScorerImpl):
    @classmethod
    def smaller_is_better(cls) -> bool:
        return True

    def _calculate_score(self, box1: BoxType, box2: BoxType) -> float:
        return (
            np.linalg.norm(box1.position - box2.position)
            if isinstance(box1, Box3D)
            else np.linalg.norm(box1.center - box2.center)
        )


class PlaneDistance(MatchingScorerImpl):
    @classmethod
    def smaller_is_better(cls) -> bool:
        return True

    def _calculate_score(self, box1: Box3D, box2: Box3D) -> float:
        pass


class Iou2D(MatchingScorerImpl):
    @classmethod
    def smaller_is_better(cls) -> bool:
        return False

    def _calculate_score(self, box1: BoxType, box2: BoxType) -> float:
        pass


class Iou3D(MatchingScorerImpl):
    @classmethod
    def smaller_is_better(cls) -> bool:
        return False

    def _calculate_score(self, box1: Box3D, box2: Box3D) -> float:
        pass


MatchingScorerLike = TypeVar("MatchingScorer", bound=MatchingScorerImpl)

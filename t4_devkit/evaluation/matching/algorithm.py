from __future__ import annotations

from abc import ABC, abstractmethod
from copy import deepcopy
from typing import TYPE_CHECKING, Sequence, TypeVar

import numpy as np

from t4_devkit.evaluation.result import PerceptionBoxResult

if TYPE_CHECKING:
    from t4_devkit.dataclass import BoxType
    from t4_devkit.typing import NDArrayF64

    from .policy import MatchingPolicyLike
    from .scorer import MatchingScorerLike

__all__ = ["GreedyMatching", "MatchingAlgorithmLike"]


class MatchingAlgorithmImpl(ABC):
    def __init__(
        self,
        scorer: MatchingScorerLike,
        policy: MatchingPolicyLike,
        matchable_threshold: float,
    ) -> None:
        super().__init__()
        self._scorer = scorer
        self._policy = policy
        self._matchable_threshold = matchable_threshold

    def _score_table(
        self,
        estimations: Sequence[BoxType],
        ground_truths: Sequence[BoxType],
    ) -> NDArrayF64:
        """Create a score table.

        Args:
            estimations (Sequence[BoxType]): Sequence of estimations.
            ground_truths (Sequence[BoxType]): Sequence of ground truths.

        Returns:
            NDArrayF64: Score table in the shape of (NumEst, NumGT).
        """
        num_rows, num_cols = len(estimations), len(ground_truths)

        table: NDArrayF64 = np.full((num_rows, num_cols), fill_value=np.nan)
        for i, box1 in enumerate(estimations):
            for j, box2 in enumerate(ground_truths):
                if box1.frame_id != box2.frame_id:
                    continue

                score = self._scorer(box1, box2)

                # check if boxes distance and label is matchable
                if self._scorer.is_better_than(
                    score, self._matchable_threshold
                ) and self._policy.is_matchable(box1, box2):
                    table[i, j] = score

        return table

    def _get_indices(self, score_table: NDArrayF64) -> tuple[int, int]:
        """Return indices of estimation and ground truth in the score table at the best score.

        Args:
            score_table (NDArrayF64): Score table in the shape of (NumEst, NumGt).

        Returns:
            Estimation index and ground truth index.
        """
        estimation_idx, ground_truth_idx = (
            np.unravel_index(np.nanargmin(score_table), score_table.shape)
            if self._scorer.smaller_is_better()
            else np.unravel_index(np.nanargmax(score_table), score_table.shape)
        )
        return estimation_idx, ground_truth_idx

    @abstractmethod
    def _do_matching(
        self,
        estimations: Sequence[BoxType],
        ground_truths: Sequence[BoxType],
        score_table: NDArrayF64,
    ) -> list[PerceptionBoxResult]:
        pass

    def __call__(
        self,
        estimations: Sequence[BoxType],
        ground_truths: Sequence[BoxType],
    ) -> list[PerceptionBoxResult]:
        score_table = self._score_table(estimations, ground_truths)
        return self._do_matching(score_table)


class GreedyMatching(MatchingAlgorithmImpl):
    def _do_matching(
        self,
        estimations: Sequence[BoxType],
        ground_truths: Sequence[BoxType],
        score_table: NDArrayF64,
    ) -> list[PerceptionBoxResult]:
        tmp_estimations = list(deepcopy(estimations))
        tmp_ground_truths = list(deepcopy(ground_truths))

        output: list[PerceptionBoxResult] = []
        # 1. Matching the nearest matchable estimations and GTs
        num_estimations, *_ = score_table.shape
        for _ in range(num_estimations):
            if np.isnan(score_table).all():
                break

            estimation_idx, ground_truth_idx = self._get_indices(score_table)

            estimation_picked = tmp_estimations.pop(estimation_idx)
            ground_truth_picked = tmp_ground_truths.pop(ground_truth_idx)
            output.append(PerceptionBoxResult(estimation_picked, ground_truth_picked))

            # Remove picked estimations and GTs
            score_table = np.delete(score_table, estimation_idx, axis=0)
            score_table = np.delete(score_table, ground_truth_idx, axis=0)

        output += [PerceptionBoxResult(estimation) for estimation in tmp_estimations]

        return output


MatchingAlgorithmLike = TypeVar("MatchingAlgorithmLike", bound=MatchingAlgorithmImpl)

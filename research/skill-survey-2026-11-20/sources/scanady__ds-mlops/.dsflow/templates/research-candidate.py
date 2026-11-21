"""Candidate model for one autoresearch session. This is the only file the agent edits.

May change: the estimator, its settings, the preprocessing steps, and the body of
``engineer_features``.

Must not change:
- The interface: ``build_model(ctx)`` and ``engineer_features(df)``.
- Data access: do not read data files and do not use the network.
- Determinism: use ``ctx.seed`` for every random choice.
- The target: do not use the target column in ``engineer_features``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

if TYPE_CHECKING:
    from dsproject.research import ResearchContext


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Return the data frame with new feature columns.

    This function must not use the target column. The baseline returns the data unchanged.
    """
    return df


def build_model(ctx: ResearchContext) -> Pipeline:
    """Return an unfitted scikit-learn pipeline for the task in ``ctx.task``."""
    numeric = Pipeline(
        [
            ("impute", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
        ]
    )
    categorical = Pipeline(
        [
            ("impute", SimpleImputer(strategy="most_frequent")),
            ("encode", OneHotEncoder(handle_unknown="ignore")),
        ]
    )
    preprocess = ColumnTransformer(
        [
            ("numeric", numeric, list(ctx.numeric_features)),
            ("categorical", categorical, list(ctx.categorical_features)),
        ]
    )
    if ctx.task == "regression":
        estimator = Ridge(random_state=ctx.seed)
    else:
        estimator = LogisticRegression(max_iter=1000, random_state=ctx.seed)
    return Pipeline([("preprocess", preprocess), ("model", estimator)])

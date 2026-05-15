"""High-level pipeline that wires loader → differ → masker → reporter."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from envcmp.differ import DiffResult, diff
from envcmp.loader import EnvSource
from envcmp.masker import SecretMasker
from envcmp.reporter import Reporter


@dataclass
class PipelineConfig:
    """Configuration options for a comparison pipeline run."""

    show_unchanged: bool = False
    mask_secrets: bool = True
    color: bool = True
    extra_secret_patterns: List[str] = field(default_factory=list)


@dataclass
class PipelineResult:
    """Holds the diff result and rendered report from a pipeline run."""

    diff: DiffResult
    report: str


def run(
    source_a: EnvSource,
    source_b: EnvSource,
    config: Optional[PipelineConfig] = None,
) -> PipelineResult:
    """Compare two EnvSources and return a PipelineResult.

    Args:
        source_a: The baseline environment source.
        source_b: The target environment source.
        config: Optional pipeline configuration.

    Returns:
        A PipelineResult containing the diff and the rendered text report.
    """
    if config is None:
        config = PipelineConfig()

    masker = SecretMasker(extra_patterns=config.extra_secret_patterns)

    data_a = masker.mask_dict(source_a.data) if config.mask_secrets else source_a.data
    data_b = masker.mask_dict(source_b.data) if config.mask_secrets else source_b.data

    diff_result = diff(
        data_a,
        data_b,
        label_a=source_a.label,
        label_b=source_b.label,
    )

    reporter = Reporter(
        label_a=source_a.label,
        label_b=source_b.label,
        color=config.color,
    )
    report_text = reporter.render(
        diff_result,
        show_unchanged=config.show_unchanged,
    )

    return PipelineResult(diff=diff_result, report=report_text)

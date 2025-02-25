import datetime

import pytest

from coverage_comment import coverage, template


def test_get_markdown_comment(coverage_obj, diff_coverage_obj):
    result = (
        template.get_markdown_comment(
            coverage=coverage_obj,
            diff_coverage=diff_coverage_obj,
            previous_coverage_rate=0.92,
            base_template="""
        {{ previous_coverage_rate | pct }}
        {{ coverage.info.percent_covered | pct }}
        {{ diff_coverage.total_percent_covered | pct }}
        {% block foo %}foo{% endblock foo %}
        {{ marker }}
        """,
            custom_template="""{% extends "base" %}
        {% block foo %}bar{% endblock foo %}
        """,
        )
        .strip()
        .split(maxsplit=4)
    )

    expected = [
        "92%",
        "75%",
        "80%",
        "bar",
        "<!-- This comment was produced by python-coverage-comment-action -->",
    ]

    assert result == expected


def test_template(coverage_obj, diff_coverage_obj):
    result = template.get_markdown_comment(
        coverage=coverage_obj,
        diff_coverage=diff_coverage_obj,
        previous_coverage_rate=0.92,
        base_template=template.read_template_file(),
        custom_template="""{% extends "base" %}
        {% block emoji_coverage_down %}:sob:{% endblock emoji_coverage_down %}
        """,
    )
    expected = """## Coverage report
The coverage rate went from `92%` to `75%` :sob:
The branch rate is `50%`.

`80%` of new lines are covered.

<details>
<summary>Diff Coverage details (click to unfold)</summary>

### codebase/code.py
`80%` of new lines are covered (`75%` of the complete file).
Missing lines: `7`, `9`

</details>
<!-- This comment was produced by python-coverage-comment-action -->"""
    assert result == expected


def test_template_full():

    cov = coverage.Coverage(
        meta=coverage.CoverageMetadata(
            version="1.2.3",
            timestamp=datetime.datetime(2000, 1, 1),
            branch_coverage=True,
            show_contexts=False,
        ),
        info=coverage.CoverageInfo(
            covered_lines=6,
            num_statements=6,
            percent_covered=1.0,
            missing_lines=0,
            excluded_lines=0,
            num_branches=2,
            num_partial_branches=0,
            covered_branches=2,
            missing_branches=0,
        ),
        files={
            "codebase/code.py": coverage.FileCoverage(
                path="codebase/code.py",
                executed_lines=[1, 2, 5, 6, 9],
                missing_lines=[],
                excluded_lines=[],
                info=coverage.CoverageInfo(
                    covered_lines=5,
                    num_statements=6,
                    percent_covered=5 / 6,
                    missing_lines=1,
                    excluded_lines=0,
                    num_branches=2,
                    num_partial_branches=0,
                    covered_branches=2,
                    missing_branches=0,
                ),
            ),
            "codebase/other.py": coverage.FileCoverage(
                path="codebase/other.py",
                executed_lines=[1, 2, 3],
                missing_lines=[],
                excluded_lines=[],
                info=coverage.CoverageInfo(
                    covered_lines=6,
                    num_statements=6,
                    percent_covered=1.0,
                    missing_lines=0,
                    excluded_lines=0,
                    num_branches=2,
                    num_partial_branches=0,
                    covered_branches=2,
                    missing_branches=0,
                ),
            ),
        },
    )

    diff_cov = coverage.DiffCoverage(
        total_num_lines=6,
        total_num_violations=0,
        total_percent_covered=1.0,
        num_changed_lines=39,
        files={
            "codebase/code.py": coverage.FileDiffCoverage(
                path="codebase/code.py",
                percent_covered=1 / 2,
                violation_lines=[5],
            ),
            "codebase/other.py": coverage.FileDiffCoverage(
                path="codebase/other.py",
                percent_covered=1,
                violation_lines=[],
            ),
        },
    )

    result = template.get_markdown_comment(
        coverage=cov,
        diff_coverage=diff_cov,
        previous_coverage_rate=1.0,
        base_template=template.read_template_file(),
    )
    expected = """## Coverage report
The coverage rate went from `100%` to `100%` :arrow_right:
The branch rate is `100%`.

`100%` of new lines are covered.

<details>
<summary>Diff Coverage details (click to unfold)</summary>

### codebase/code.py
`50%` of new lines are covered (`83%` of the complete file).
Missing lines: `5`

### codebase/other.py
`100%` of new lines are covered (`100%` of the complete file).

</details>
<!-- This comment was produced by python-coverage-comment-action -->"""
    assert result == expected


def test_template__no_branch_no_previous(coverage_obj_no_branch, diff_coverage_obj):
    result = template.get_markdown_comment(
        coverage=coverage_obj_no_branch,
        diff_coverage=diff_coverage_obj,
        previous_coverage_rate=None,
        base_template=template.read_template_file(),
    )
    expected = """## Coverage report
The coverage rate is `75%`.

`80%` of new lines are covered.

<details>
<summary>Diff Coverage details (click to unfold)</summary>

### codebase/code.py
`80%` of new lines are covered (`75%` of the complete file).
Missing lines: `7`, `9`

</details>
<!-- This comment was produced by python-coverage-comment-action -->"""
    assert result == expected


def test_read_template_file():
    assert template.read_template_file().startswith(
        "{% block title %}## Coverage report{% endblock title %}"
    )


def test_template__no_marker(coverage_obj, diff_coverage_obj):

    with pytest.raises(template.MissingMarker):
        template.get_markdown_comment(
            coverage=coverage_obj,
            diff_coverage=diff_coverage_obj,
            previous_coverage_rate=0.92,
            base_template=template.read_template_file(),
            custom_template="""foo bar""",
        )


def test_template__broken_template(coverage_obj, diff_coverage_obj):

    with pytest.raises(template.TemplateError):
        template.get_markdown_comment(
            coverage=coverage_obj,
            diff_coverage=diff_coverage_obj,
            previous_coverage_rate=0.92,
            base_template=template.read_template_file(),
            custom_template="""{% extends "foo" %}""",
        )


def test_pct():
    assert template.pct(0.83) == "83%"


def test_uptodate():
    assert template.uptodate() is True

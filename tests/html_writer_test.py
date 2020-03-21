import pytest
from pigeonpictures import html_writer
from datetime import datetime
import re


def test_update_date_snapping_to_00():
    close_to_00 = datetime(2020, 3, 14, 12, 4)
    result_of_00 = html_writer.calculate_next_update_time(close_to_00)
    assert result_of_00 == datetime(2020, 3, 14, 12, 30)


def test_update_date_snapping_to_30():
    close_to_30 = datetime(2020, 3, 14, 12, 34)
    result_of_30 = html_writer.calculate_next_update_time(close_to_30)
    assert result_of_30 == datetime(2020, 3, 14, 13, 0)


def test_isotime_rendered_in_jinja_html():
    jinja_writer = html_writer.Jinja2HTMLWriter(
        "pigeonpictures/template.j2", "frontend/index.js"
    )
    html = jinja_writer.render(["https://http.cat/404"])
    regex = re.compile(
        'new Date\("\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d"\)'
    )  # naive regex, will do
    found = False

    for line in html.split("\n"):
        if regex.search(line) is not None:
            found = True
            break

    assert found is True

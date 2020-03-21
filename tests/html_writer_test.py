import pytest
from pigeonpictures import html_writer
from datetime import datetime


def test_update_date_snapping_to_00():
    close_to_00 = datetime(2020, 3, 14, 12, 4)
    result_of_00 = html_writer.calculate_next_update_time(close_to_00)
    assert result_of_00 == datetime(2020, 3, 14, 12, 30)


def test_update_date_snapping_to_30():
    close_to_30 = datetime(2020, 3, 14, 12, 34)
    result_of_30 = html_writer.calculate_next_update_time(close_to_30)
    assert result_of_30 == datetime(2020, 3, 14, 13, 0)

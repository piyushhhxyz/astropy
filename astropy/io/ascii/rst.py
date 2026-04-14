# Licensed under a 3-clause BSD style license
"""
:Author: Simon Gibbons (simongibbons@gmail.com)
"""


from .core import DefaultSplitter
from .fixedwidth import (
    FixedWidth,
    FixedWidthData,
    FixedWidthHeader,
    FixedWidthTwoLineDataSplitter,
)


class SimpleRSTHeader(FixedWidthHeader):
    position_line = 0
    start_line = 1
    splitter_class = DefaultSplitter
    position_char = "="

    def get_fixedwidth_params(self, line):
        vals, starts, ends = super().get_fixedwidth_params(line)
        # The right hand column can be unbounded
        ends[-1] = None
        return vals, starts, ends


class SimpleRSTData(FixedWidthData):
    start_line = 3
    end_line = -1
    splitter_class = FixedWidthTwoLineDataSplitter


class RST(FixedWidth):
    """reStructuredText simple format table.

    See: https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#simple-tables

    Example::

        ==== ===== ======
        Col1  Col2  Col3
        ==== ===== ======
          1    2.3  Hello
          2    4.5  Worlds
        ==== ===== ======

    Currently there is no support for reading tables which utilize continuation lines,
    or for ones which define column spans through the use of an additional
    line of dashes in the header.

    Parameters
    ----------
    header_rows : list, optional
        List of table rows to output as header rows in the RST table.
        The default is ``['name']``. Allowed values are any column
        attribute (e.g. ``'name'``, ``'unit'``, ``'dtype'``). For
        example, ``header_rows=['name', 'unit']`` will produce a
        two-row header with column names and units.

    """

    _format_name = "rst"
    _description = "reStructuredText simple table"
    data_class = SimpleRSTData
    header_class = SimpleRSTHeader

    def __init__(self, header_rows=None):
        super().__init__(delimiter_pad=None, bookend=False, header_rows=header_rows)
        # Adjust data start_line based on header_rows length. The RST format
        # has a separator line (=====) before and after the header rows, so the
        # data starts at: 1 (opening separator) + len(header_rows) + 1 (closing
        # separator) = len(header_rows) + 2.
        self.data.start_line = len(self.header.header_rows) + 2

    def write(self, lines):
        lines = super().write(lines)
        # Index of the separator line (=====) in the parent's output. The
        # parent writes header_rows followed by the position/separator line,
        # so the separator is at index len(header_rows).
        idx = len(self.header.header_rows)
        lines = [lines[idx]] + lines + [lines[idx]]
        return lines

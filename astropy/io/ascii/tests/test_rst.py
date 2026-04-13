# Licensed under a 3-clause BSD style license - see LICENSE.rst

from io import StringIO

from astropy.io import ascii

from .common import assert_almost_equal, assert_equal


def assert_equal_splitlines(arg1, arg2):
    assert_equal(arg1.splitlines(), arg2.splitlines())


def test_read_normal():
    """Normal SimpleRST Table"""
    table = """
# comment (with blank line above)
======= =========
   Col1      Col2
======= =========
   1.2    "hello"
   2.4  's worlds
======= =========
"""
    reader = ascii.get_reader(Reader=ascii.RST)
    dat = reader.read(table)
    assert_equal(dat.colnames, ["Col1", "Col2"])
    assert_almost_equal(dat[1][0], 2.4)
    assert_equal(dat[0][1], '"hello"')
    assert_equal(dat[1][1], "'s worlds")


def test_read_normal_names():
    """Normal SimpleRST Table with provided column names"""
    table = """
# comment (with blank line above)
======= =========
   Col1      Col2
======= =========
   1.2    "hello"
   2.4  's worlds
======= =========
"""
    reader = ascii.get_reader(Reader=ascii.RST, names=("name1", "name2"))
    dat = reader.read(table)
    assert_equal(dat.colnames, ["name1", "name2"])
    assert_almost_equal(dat[1][0], 2.4)


def test_read_normal_names_include():
    """Normal SimpleRST Table with provided column names"""
    table = """
# comment (with blank line above)
=======  ========== ======
   Col1     Col2      Col3
=======  ========== ======
   1.2     "hello"       3
   2.4    's worlds      7
=======  ========== ======
"""
    reader = ascii.get_reader(
        Reader=ascii.RST,
        names=("name1", "name2", "name3"),
        include_names=("name1", "name3"),
    )
    dat = reader.read(table)
    assert_equal(dat.colnames, ["name1", "name3"])
    assert_almost_equal(dat[1][0], 2.4)
    assert_equal(dat[0][1], 3)


def test_read_normal_exclude():
    """Nice, typical SimpleRST table with col name excluded"""
    table = """
======= ==========
  Col1     Col2
======= ==========
  1.2     "hello"
  2.4    's worlds
======= ==========
"""
    reader = ascii.get_reader(Reader=ascii.RST, exclude_names=("Col1",))
    dat = reader.read(table)
    assert_equal(dat.colnames, ["Col2"])
    assert_equal(dat[1][0], "'s worlds")


def test_read_unbounded_right_column():
    """The right hand column should be allowed to overflow"""
    table = """
# comment (with blank line above)
===== ===== ====
 Col1  Col2 Col3
===== ===== ====
 1.2    2    Hello
 2.4     4   Worlds
===== ===== ====
"""
    reader = ascii.get_reader(Reader=ascii.RST)
    dat = reader.read(table)
    assert_equal(dat[0][2], "Hello")
    assert_equal(dat[1][2], "Worlds")


def test_read_unbounded_right_column_header():
    """The right hand column should be allowed to overflow"""
    table = """
# comment (with blank line above)
===== ===== ====
 Col1  Col2 Col3Long
===== ===== ====
 1.2    2    Hello
 2.4     4   Worlds
===== ===== ====
"""
    reader = ascii.get_reader(Reader=ascii.RST)
    dat = reader.read(table)
    assert_equal(dat.colnames[-1], "Col3Long")


def test_read_right_indented_table():
    """We should be able to read right indented tables correctly"""
    table = """
# comment (with blank line above)
   ==== ==== ====
   Col1 Col2 Col3
   ==== ==== ====
    3    3.4  foo
    1    4.5  bar
   ==== ==== ====
"""
    reader = ascii.get_reader(Reader=ascii.RST)
    dat = reader.read(table)
    assert_equal(dat.colnames, ["Col1", "Col2", "Col3"])
    assert_equal(dat[0][2], "foo")
    assert_equal(dat[1][0], 1)


def test_trailing_spaces_in_row_definition():
    """Trailing spaces in the row definition column shouldn't matter"""
    table = (
        "\n"
        "# comment (with blank line above)\n"
        "   ==== ==== ====    \n"
        "   Col1 Col2 Col3\n"
        "   ==== ==== ====  \n"
        "    3    3.4  foo\n"
        "    1    4.5  bar\n"
        "   ==== ==== ====  \n"
    )
    # make sure no one accidentally deletes the trailing whitespaces in the
    # table.
    assert len(table) == 151

    reader = ascii.get_reader(Reader=ascii.RST)
    dat = reader.read(table)
    assert_equal(dat.colnames, ["Col1", "Col2", "Col3"])
    assert_equal(dat[0][2], "foo")
    assert_equal(dat[1][0], 1)


table = """\
====== =========== ============ ===========
  Col1    Col2        Col3        Col4
====== =========== ============ ===========
  1.2    "hello"      1           a
  2.4   's worlds          2           2
====== =========== ============ ===========
"""
dat = ascii.read(table, Reader=ascii.RST)


def test_write_normal():
    """Write a table as a normal SimpleRST Table"""
    out = StringIO()
    ascii.write(dat, out, Writer=ascii.RST)
    assert_equal_splitlines(
        out.getvalue(),
        """\
==== ========= ==== ====
Col1      Col2 Col3 Col4
==== ========= ==== ====
 1.2   "hello"    1    a
 2.4 's worlds    2    2
==== ========= ==== ====
""",
    )


def test_write_header_rows():
    """Write a table as a SimpleRST Table with header_rows"""
    from astropy.table import QTable
    import astropy.units as u

    tbl = QTable({"wave": [350, 950] * u.nm, "response": [0.7, 1.2] * u.count})

    # Test with header_rows=["name", "unit"]
    out = StringIO()
    ascii.write(tbl, out, Writer=ascii.RST, header_rows=["name", "unit"])
    assert_equal_splitlines(
        out.getvalue(),
        """\
===== ========
 wave response
   nm       ct
===== ========
350.0      0.7
950.0      1.2
===== ========
""",
    )

    # Test that header_rows=["name"] gives the same output as default
    out_default = StringIO()
    ascii.write(tbl, out_default, Writer=ascii.RST)
    out_explicit = StringIO()
    ascii.write(tbl, out_explicit, Writer=ascii.RST, header_rows=["name"])
    assert_equal_splitlines(out_default.getvalue(), out_explicit.getvalue())


def test_rst_with_header_rows():
    """Round-trip a table with header_rows specified"""
    import numpy as np
    import astropy.units as u
    from astropy.table import QTable

    lines = [
        "======= ======== ====",
        "   wave response ints",
        "     nm       ct     ",
        "float64  float32 int8",
        "======= ======== ====",
        "  350.0      1.0    1",
        "  950.0      2.0    2",
        "======= ======== ====",
    ]
    tbl = QTable.read(lines, format="ascii.rst", header_rows=["name", "unit", "dtype"])
    assert tbl["wave"].unit == u.nm
    assert tbl["response"].unit == u.ct
    assert tbl["wave"].dtype == np.float64
    assert tbl["response"].dtype == np.float32
    assert tbl["ints"].dtype == np.int8

    out = StringIO()
    tbl.write(out, format="ascii.rst", header_rows=["name", "unit", "dtype"])
    assert out.getvalue().splitlines() == lines

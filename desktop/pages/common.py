from PyQt5 import QtWidgets


def fill_table(table: QtWidgets.QTableWidget, rows: list[dict], columns: list[tuple[str, str]]):
    table.clear()
    table.setColumnCount(len(columns))
    table.setHorizontalHeaderLabels([title for _, title in columns])
    table.setRowCount(len(rows))
    for row_index, row in enumerate(rows):
        for column_index, (key, _) in enumerate(columns):
            value = row.get(key, "")
            table.setItem(row_index, column_index, QtWidgets.QTableWidgetItem(str(value if value is not None else "")))
    table.resizeColumnsToContents()
    table.horizontalHeader().setStretchLastSection(True)

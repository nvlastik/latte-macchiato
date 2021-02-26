from PyQt5 import uic, QtWidgets  # Импортируем uic
import sqlite3
from PyQt5.Qt import *
from PyQt5.QtWidgets import QMessageBox
from UI.main import *
from UI.addEditCoffeeForm import *


class Table(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.btn_add.clicked.connect(self.add)
        self.btn_edit.clicked.connect(self.edit)
        self.model = QStandardItemModel()
        self.table.setModel(self.model)
        self.con = sqlite3.connect("coffee.sqlite")  # БД
        self.cur = self.con.cursor()
        self.load_data()

    def add(self):
        a = Edit_table(self, variety=self.ob, degree=["В зернах", "Молотый"])
        a.show()

    def edit(self):
        selct = [i.row() for i in self.table.selectionModel().selectedRows()]
        if selct == []:
            QMessageBox.critical(self, "Ошибка ", "Выделите строчку которую хотите изменить", QMessageBox.Ok)

        for st in selct:
            el = self.zap[st]
            a = Edit_table(self, el[1], self.ob, ["В зернах", "Молотый"] if el[3] == 1 else ["Молотый", "В зернах"], el[4], el[5], el[6], el[0])
            a.show()


    def closeEvent(self, event):
        self.con.close()  # закрытие БД при завершении работы

    def load_data(self):
        self.ob = {o[0]: o[1] for o in self.cur.execute("SELECT * FROM roasting").fetchall()}  # степени обжарки
        self.zap = self.cur.execute("SELECT * FROM coffee").fetchall()
        vsv = [(i[0], i[1], self.ob[i[2]], "В зернах" if i[3] else "Молотый", i[4], f"{i[5]} г.", f"{i[6]} руб.") for i in self.zap]  # подготовка к выводу
        self.model.setHorizontalHeaderLabels(["id", "Название", "Степень обжарки", "Вид", "Описание", "Вес", "Цена"])

        for i in range(len(vsv)):  # вывод данных
            for j in range(len(vsv[i])):
                item = QStandardItem(str(vsv[i][j]))
                self.model.setItem(i, j, item)

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)  # делаем красиво
        self.table.horizontalHeader().setMinimumSectionSize(0)


class Edit_table(QMainWindow, Add_item):
    def __init__(self, sl, name="", variety={}, degree=[], description="", volume=0, price=0, id=None):
        super().__init__(sl)
        self.setupUi(self)
        self.sl = sl
        self.id = id
        self.variety = {}
        for i, j in variety.items():
            self.variety[j] = i
        uic.loadUi('addEditCoffeeForm.ui', self)  # Загружаем дизай
        self.l_name.setText(name)
        self.cmb_variety.addItems(variety.values())
        self.cmb_degree.addItems(degree)
        self.l_description.setText(description)
        self.spb_volume.setValue(volume)
        self.spb_price.setValue(price)
        self.btnb.accepted.connect(self.acc)
        self.btnb.rejected.connect(self.ex)
        self.vsv = None

    def acc(self):
        if self.id:
            self.sl.cur.execute("UPDATE coffee SET variety=?, degree=?, grains=?, description=?, volume=?, price=? WHERE id=?",
                                (self.l_name.text(),
                                 self.variety[self.cmb_variety.currentText()],
                                 1 if self.cmb_degree == "В зернах" else 0,
                                 self.l_description.text(),
                                 self.spb_volume.value(),
                                 self.spb_price.value(),
                                 self.id))
        else:
            self.sl.cur.execute("INSERT INTO coffee(variety, degree, grains, description, volume, price) VALUES(?, ?, ?, ?, ?, ?)",
                                (self.l_name.text(),
                                 self.variety[self.cmb_variety.currentText()],
                                 1 if self.cmb_degree == "В зернах" else 0,
                                 self.l_description.text(),
                                 self.spb_volume.value(),
                                 self.spb_price.value()))

        self.sl.con.commit()
        self.sl.load_data()
        self.ex()

    def ex(self):
        self.hide()


if __name__ == "__main__":
    app = QApplication([])
    w = Table()
    w.show()
    app.exec_()
import sys
import torch
from form import*

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = UiEntry()
    window.show()
    sys.exit(app.exec_())

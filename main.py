import sys
from PyQt5.QtWidgets import QApplication
from GIU import BusDepotApp

def main():
    app = QApplication(sys.argv)
    
    # Настройка стиля
    app.setStyle('Fusion')
    
    window = BusDepotApp()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
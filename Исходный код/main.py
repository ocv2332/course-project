import sys

from PyQt5 import QtWidgets

from config.config_parser import ConfigParser
from database.database import DataBase
from exceptions import Exceptions
from gui.connection.auth_connection import AuthWindow
from utils import ParserUtils, SecurityUtils, SecondaryUtils
from utils.gui_utils import GuiUtils


def main():
    config = ConfigParser("config/config.ini")
    parser_utils = ParserUtils(config)
    security_utils = SecurityUtils(config)
    secondary_utils = SecondaryUtils()
    gui_utils = GuiUtils()
    exceptions = Exceptions(config)

    database = DataBase("database.sqlite3", config, parser_utils, security_utils, exceptions)
    database.create_all_tables()

    app = QtWidgets.QApplication(sys.argv)
    window = AuthWindow(config, database, exceptions, parser_utils, security_utils, secondary_utils, gui_utils)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

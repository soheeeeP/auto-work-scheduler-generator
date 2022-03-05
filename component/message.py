from PyQt5.QtWidgets import QMessageBox


def setAboutMessageBox(window, message):
    message_box = QMessageBox.about(window, "QMessageBox", message)
    return


def setCriticalMessageBox(window, message):
    message_box = QMessageBox.critical(window, "QMessageBox", message, QMessageBox.Close)
    return


def setQuestionMessageBox(window, message) -> bool:
    message_box = QMessageBox.question(window, "QMessageBox", message, QMessageBox.No | QMessageBox.Yes)

    if message_box == QMessageBox.No:
        return False
    return True


def setInformationMessageBox(window, title, message) -> bool:
    message_box = QMessageBox.information(window, title, message, QMessageBox.Yes | QMessageBox.Cancel)

    if message_box == QMessageBox.Cancel:
        return False
    return True


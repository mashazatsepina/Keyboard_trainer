from PyQt6.QtGui import QKeyEvent
from PyQt6.QtCore import Qt, QSize, QTimer, QTime
from PyQt6.QtWidgets import QMainWindow, QPushButton, QLabel, QFileDialog, QLineEdit, QWidget
from src.text_generating import text_generate
from src.add_attempt import add_attempt
from src.alignments_list import alignments_list
from src.globals import *

class MainWindow(QMainWindow):

    def __init__(self) -> None:
        """ Sets window parameters and launches the start menu """
        super().__init__()
        self.setWindowTitle("Keyboard Trainer")
        self.setFixedSize(QSize(1400, 900))
        self.main_menu()
        self.button_exit = self.create_button("exit", 1150, 50, 200, 60, 28)
        self.button_exit.clicked.connect(self.close)
    
    def main_menu(self) -> None:
        """ Displays the start menu page """
        self.button15 = self.create_button('15 sec', 550, 200, 300, 80, 32)
        self.button30 = self.create_button('30 sec', 550, 300, 300, 80, 32)
        self.button60 = self.create_button('60 sec', 550, 400, 300, 80, 32)
        self.button_user = self.create_button('user mode', 550, 500, 300,
                                              80, 32)
        self.button_stat = self.create_button('statistics', 550, 600, 300,
                                              80, 32)
        self.time_limit = 0
        self.user_mode = False
        self.button15.clicked.connect(self.set_mode(self.switch_to_mode, 15))
        self.button30.clicked.connect(self.set_mode(self.switch_to_mode, 30))
        self.button60.clicked.connect(self.set_mode(self.switch_to_mode, 60))
        self.button_user.clicked.connect(self.set_mode(
            self.switch_to_mode, 0))
        self.button_stat.clicked.connect(self.open_stat_page)
        self.is_launched = False

    def launch(self) -> None:
        """ Creates an attempt window, allows the user typing """
        self.is_launched = False
        self.countdown()
        self.count_signs = 0
        self.mistakes = 0
        self.label_countdown.hide()

        self.timer = QTimer()
        self.timer.setInterval(10)
        self.timer.timeout.connect(self.update_time)
        self.start_time = QTime(0, 0, 0, 0)
        self.current_time = self.start_time

        self.label_time = self.create_label(600, 350, 200, 100, 24, 'centre')
        self.label_str1 = self.create_label(200, 450, 500, 80, 40, 'right')
        self.label_str1.setStyleSheet("color: rgb(35, 45, 130)")
        self.label_str2 = self.create_label(700, 450, 500, 80, 40, 'left')
        self.label_str2.setStyleSheet("color: rgb(150, 150, 150)")

        self.string1 = ''
        self.string2 = text_generate()
        self.label_str1.setText(self.string1)
        self.label_str2.setText(self.string2)

        self.label_mistakes = self.create_label(800, 550, 400, 80, 24,
                                                'right')
        self.label_mistakes.setStyleSheet("color: rgb(170, 20, 35)")
        self.label_mistakes.setText("mistakes: " + "0")
        self.is_mistake = False

        self.button_exit.hide()
        self.button_exit.setEnabled(False)
        self.label_enter = self.create_label(550, 800, 400, 80, 14, 'centre')
        self.label_enter.setText("press enter to pause")

    def update_time(self) -> None:
        """ Updates the attempt timer """
        if not self.is_launched:
            return
        self.current_time = self.current_time.addMSecs(self.timer.interval())
        self.label_time.setText(self.current_time.toString("mm:ss.zzz"))
        if self.time_limit < self.current_time:
            self.end_attempt()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """ Handles keystrokes when the user is typing """
        if not self.is_launched:
            return

        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            self.pause()
            return

        if (event.text() != self.string2[0] and
            not (event.text() == 'е' and self.string2[0] == 'ё')):
            self.label_str2.setStyleSheet(
                "background-color: rgb(220, 85, 85); color: rgb(150, 150, 150)")
            if not self.is_mistake:
                self.mistakes += 1
                self.label_mistakes.setText("mistakes: " + str(self.mistakes))
            self.is_mistake = True
            return
        self.is_mistake = False
        self.count_signs += 1
        self.label_str2.setStyleSheet("color: rgb(150, 150, 150)")
        self.string1 += self.string2[0]
        self.string2 = self.string2[1:]
        self.label_str1.setText(self.string1)
        self.label_str2.setText(self.string2)

    def end_attempt(self) -> None:
        """ Fixes the results of the attempt and
    switches to the attempt statistics page """
        self.attempt_time = self.current_time
        self.is_launched = False
        self.hide_labels(self.label_time, self.label_str1, self.label_str2,
                         self.label_mistakes, self.label_enter)
        self.button_exit.setEnabled(True)
        self.button_exit.show()
        self.attempt_stat()

    def hide_stat_attempt(self) -> None:
        """ Disables widgets from the attempt statistics page"""
        self.hide_labels(self.label_result, self.label_accuracy,
                         self.label_speed, self.label_done, self.label_failed)
        self.hide_buttons(self.button_restart, self.button_to_menu)

    def user_task_selection(self) -> None:
        """ Displays the user tasks page """
        self.button_new_task = self.create_button("create task", 600, 300,
                                                   300, 80, 32)
        self.button_new_task.clicked.connect(self.create_task_page)
        self.button_upload = self.create_button("upload task", 600, 400, 300,
                                                80, 32)
        self.button_upload.clicked.connect(self.file_selection)
        self.button_to_menu = self.create_button("menu", 600, 500, 300,
                                                 80, 32)
        self.button_to_menu.clicked.connect(
            self.back_from_user_task_selection(self.main_menu))


    def file_selection(self) -> None:
        """ Opens the file selection window,
    reads the task parameters from the file """
        file_dialog = QFileDialog(self)
        file_path = file_dialog.getOpenFileName(None, "Open", "", "*.txt")[0]
        if file_path:
            with open(file_path, 'r') as file:
                try:
                    self.time_limit = int(file.readline())
                    self.speed_goal = int(file.readline())
                except:
                    self.button_upload.setChecked(False)
                    return
        else:
            self.button_upload.setChecked(False)
            return
        self.hide_buttons(self.button_new_task, self.button_upload,
                          self.button_to_menu)
        self.task_info_page()
        
    def task_info_page(self) -> None:
        """ Shows the user the task parameters """
        self.label_task = self.create_label(500, 250, 400, 100, 52, 'centre')
        self.label_task_speed = self.create_label(450, 350, 400, 100, 32,
                                                  'left')
        self.label_task_time = self.create_label(450, 400, 400, 100, 32,
                                                 'left')
        self.label_task.setText("Task:")
        self.label_task_speed.setText("Speed: " + str(self.speed_goal) +
                                      " wpm")
        self.label_task_time.setText("Time: " + str(self.time_limit) + " sec")
        self.time_limit = QTime(0, 0, 0, 0).addSecs(self.time_limit)
        self.button_start_task = self.create_button("start", 350, 550, 300,
                                                    80, 32)
        self.button_to_menu = self.create_button("menu", 750, 550, 300,
                                                 80, 32)
        self.button_start_task.clicked.connect(self.launch_task(self.launch))
        self.button_to_menu.clicked.connect(self.back_from_task_info(
            self.main_menu))

    def create_task_page(self) -> None:
        """ Displays the page where the user creates the task """
        self.hide_buttons(self.button_new_task, self.button_upload,
                          self.button_to_menu)
        self.label_input_speed = self.create_label(350, 250, 300, 80, 32,
                                                   'centre')
        self.label_input_speed.setText("speed: ")
        self.label_input_time = self.create_label(750, 250, 300, 80, 32,
                                                  'centre')
        self.label_input_time.setText("time:")
        self.edit_speed = self.create_line_edit(350, 350, 300, 80, 32)
        self.edit_time = self.create_line_edit(750, 350, 300, 80, 32)

        self.button_go = self.create_button("go!", 550, 500, 300, 80, 32)
        self.button_go.clicked.connect(self.start_create_task)

        self.button_get_file = self.create_button("get a file", 550, 600, 300,
                                                  80, 32)
        self.button_get_file.clicked.connect(self.get_file)
        self.button_to_menu = self.create_button("menu", 550, 700, 300,
                                                 80, 32)
        self.button_to_menu.clicked.connect(self.back_from_create_task(
            self.main_menu))

    def hide_create_task_page(self) -> None:
        """ Disables widgets from the creating task page """
        self.hide_labels(self.label_input_speed, self.label_input_time)
        self.hide_buttons(self.button_go, self.button_get_file,
                          self.button_to_menu)
        self.edit_speed.hide()
        self.edit_speed.setEnabled(False)
        self.edit_time.hide()
        self.edit_time.setEnabled(False)

    def get_file(self) -> None:
        """ Saves the created task to the selected folder """
        if self.edit_speed.text() and self.edit_time.text():
            file_dialog = QFileDialog(self)
            file_name, _ = file_dialog.getSaveFileName(
                self, "Save the task", "", "(*.txt)")
            self.speed_goal = int(self.edit_speed.text())
            self.time_limit = QTime(0, 0, 0, 0).addSecs(
                int(self.edit_time.text()))
            if file_name:
                with open(file_name, "w") as file:
                    file.write(str(self.time_limit.second()) + '\n')
                    file.write(str(self.speed_goal))
        self.button_get_file.setChecked(False)
        return

    def start_create_task(self) -> None:
        """ Sets user settings """
        if self.edit_speed.text() and self.edit_time.text():
            self.speed_goal = int(self.edit_speed.text())
            self.time_limit = QTime(0, 0, 0, 0).addSecs(
                int(self.edit_time.text()))
            self.hide_create_task_page()
            self.launch()
        else:
            self.button_go.setChecked(False)
            return

    def attempt_stat(self) -> None:
        """ Counts and displays the results of the attempt """
        self.label_result = self.create_label(500, 250, 400, 100, 52,
                                              'centre')
        self.label_speed = self.create_label(450, 350, 400, 100, 32, 'left')
        self.label_accuracy = self.create_label(450, 400, 400, 100, 32,
                                                'left')
        self.label_result.setText("Your result:")

        if self.count_signs == 0:
            self.res_speed = 0
            self.accuracy = 0
            self.label_speed.setText("speed: 0 wpm")
            self.label_accuracy.setText("accuracy: 0%")
        else:
            res_time = self.start_time.msecsTo(self.attempt_time) / mil_per_min
            self.res_speed = round(self.count_signs / res_time / average_len, 2)
            self.label_speed.setText("speed: " + str(self.res_speed) + " wpm")
            self.accuracy = round((1 - self.mistakes / self.count_signs)
                                  * 100, 2)
            self.label_accuracy.setText("accuracy: " + str(self.accuracy)
                                        + "%")

        self.button_to_menu = self.create_button("menu", 550, 600, 300,
                                                 80, 32)
        self.button_restart = self.create_button("restart", 550, 700, 300,
                                                 80, 32)
        self.button_restart.clicked.connect(self.restart_task(self.launch))
        self.button_to_menu.clicked.connect(self.back_from_res(
            self.main_menu))
        self.label_done = self.create_label(500, 500, 400, 100, 52, 'centre')
        self.label_failed = self.create_label(500, 500, 400, 100, 52,
                                              'centre')
        if self.user_mode:
            self.check_res()
        add_attempt(self.time_limit.second(), self.res_speed, self.accuracy) 

    def countdown(self) -> None:
        """ Starts the countdown """
        self.label_countdown = self.create_label(600, 350, 200, 100, 80,
                                                 'centre')
        self.seconds_left = seconds_left
        self.timer_count = QTimer(self)
        self.timer_count.setInterval(mil_per_sec)
        self.timer_count.timeout.connect(self.update_timer_count)
        self.timer_count.start()

    def update_timer_count(self) -> None:
        """ Updates countdown timer with the set interval
    and at the end launches an attempt"""
        self.label_countdown.setText(str(self.seconds_left))
        self.label_countdown.show()
        self.seconds_left -= 1
        if self.seconds_left == -1:
            self.timer_count.stop()
            self.label_countdown.hide()
            self.label_time.show()
            self.timer.start()
            self.is_launched = True  

    def hide_task_info_page(self) -> None:
        """ Disables widgets from the task information page """
        self.hide_buttons(self.button_start_task, self.button_to_menu)
        self.hide_labels(self.label_task, self.label_task_speed,
                         self.label_task_time) 

    def back_from_task_info(self, main_menu):
        """ Goes to the main menu from the task information page """ 
        def wrapped():
            self.hide_task_info_page()
            main_menu()
        return wrapped
    
    def back_from_res(self, main_menu):
        """ Goes to the main menu from the task result page """
        def wrapped():
            self.hide_stat_attempt()
            main_menu()
        return wrapped
    
    def back_from_stat(self, main_menu):
        """ Goes to the main menu from the user's statistics page """
        def wrapped():
            self.hide_labels(self.label_stat, self.label_last_attempts)
            self.button_to_menu.hide()
            main_menu()
        return wrapped
    
    def back_from_user_task_selection(self, main_menu):
        """ Goes to the main menu from the user task selection page """
        def wrapped():
            self.hide_buttons(self.button_to_menu, self.button_new_task,
                              self.button_upload)
            main_menu()
        return wrapped
    
    def back_from_create_task(self, main_menu):
        """ Goes to the main menu from create task page """
        def wrapped():
            self.hide_create_task_page()
            main_menu()
        return wrapped

    def back_from_pause(self, main_menu):
        """ Goes to the main menu from pause page """
        def wrapped():
            self.hide_labels(self.label_pause, self.label_time)
            self.hide_buttons(self.button_continue, self.button_to_menu)
            main_menu()
        return wrapped          

    def launch_task(self, launch):
        """ Starts the attempt """
        def wrapped():
            self.hide_task_info_page()
            launch()
        return wrapped
    
    def restart_task(self, launch):
        """ Disables widgets and restarts the attempt """
        def wrapped():
            self.hide_stat_attempt()
            launch()
        return wrapped

    def check_res(self) -> None:
        """ Checks whether the user has completed the task
    successfully and displays the result """
        if self.res_speed >= self.speed_goal:
            self.label_done.setText("Completed!")
            self.label_done.setStyleSheet("color: rgb(10, 115, 45)")
        else:
            self.label_failed.setText("Failed!")
            self.label_failed.setStyleSheet("color: rgb(170, 20, 35)")

    def set_mode(self, switch_to_mode, time_limit: int):
        """ Sets the mode and relevant limits """
        def wrapped():
            self.user_mode = not bool(time_limit)
            self.time_limit = QTime(0, 0, 0, 0).addSecs(time_limit)
            return switch_to_mode()
        return wrapped

    def switch_to_mode(self) -> None:
        """ Launches a new attempt or goes to the user tasks page """
        self.hide_buttons(self.button15, self.button30, self.button60,
                          self.button_user, self.button_stat)
        if self.user_mode:
            self.user_task_selection()
        else:
            self.launch()

    def open_stat_page(self) -> None:
        """ Displays the user's statistics page with information
    about the last 10 attempts """
        self.hide_buttons(self.button15, self.button30, self.button60,
                          self.button_user, self.button_stat)
        self.label_last_attempts = self.create_label(450, 80, 500, 80, 32,
                                                     'centre')
        self.label_last_attempts.setText("Last 10 attempts:")
        self.label_stat = self.create_label(200, 200, 1000, 500, 32, 'left')
        self.label_stat.setWordWrap(True)
        with open("src/attempts.txt", "r") as file:
            self.label_stat.setText(file.read())
        self.button_to_menu = self.create_button("menu", 550, 750, 300,
                                                 80, 32)
        self.button_to_menu.clicked.connect(self.back_from_stat(
            self.main_menu))

    def hide_buttons(self, *args: QLabel) -> None:
        """ Disable all buttons """
        for button in args:
            button.setEnabled(False)
            button.hide()

    def hide_labels(self, *args: QLabel) -> None:
        """ Hides all labels """
        for label in args:
            label.hide()

    def create_label(self, pos_weight: int,
                     pos_height: int, size_weight: int,
                     size_height: int, point_size: int, align: str) -> QLabel:
        """ Creates label and sets its parameters """
        label = QLabel(self)
        label.move(pos_weight, pos_height)
        label.resize(size_weight, size_height)
        font = label.font()
        font.setPointSize(point_size)
        label.setFont(font)
        label.setAlignment(alignments_list[align])
        label.show()
        return label

    def create_button(self, title: str, pos_weight: int,
                     pos_height: int, size_weight: int,
                     size_height: int, point_size: int) -> QPushButton:
        """ Creates button and sets its parameters"""
        button = QPushButton(title, self)
        button.move(pos_weight, pos_height)
        button.resize(size_weight, size_height)
        font = button.font()
        font.setPointSize(point_size)
        button.setFont(font)
        button.setCheckable(True)
        button.show()
        return button
    
    def create_line_edit(self, pos_weight: int,
                         pos_height: int, size_weight: int,
                         size_height: int, point_size: int) -> QLineEdit:
        """ Create LineEdit and sets its parameters """
        edit_line = QLineEdit(self)
        font = edit_line.font()
        font.setPointSize(point_size)
        edit_line.setFont(font)
        edit_line.show()
        edit_line.move(pos_weight, pos_height)
        edit_line.resize(size_weight, size_height)
        return edit_line

    def pause(self) -> None:
        """ Pauses the attempt """
        self.timer.stop()
        self.is_launched = False
        self.hide_labels(self.label_str1, self.label_str2,
                         self.label_mistakes, self.label_enter)
        self.label_pause = self.create_label(550, 450, 300, 80, 52, 'centre')
        self.label_pause.setText("pause")
        self.button_continue = self.create_button("continue", 550, 600, 300,
                                                  80, 32)
        self.button_continue.clicked.connect(self.continue_attempt)
        self.button_to_menu = self.create_button("menu", 550, 700, 300,
                                                 80, 32)
        self.button_to_menu.clicked.connect(self.back_from_pause(
            self.main_menu))
        self.button_exit.show()
        self.button_exit.setEnabled(True)

    def continue_attempt(self) -> None:
        """ Continues the attempt after a pause """
        self.hide_labels(self.label_pause, self.label_time)
        self.hide_buttons(self.button_continue, self.button_to_menu,
                          self.button_exit)
        self.timer.start()
        self.countdown()
        self.label_str1.show()
        self.label_str2.show()
        self.label_mistakes.show() 
        self.label_enter.show()

    def close(self) -> None:
        """ Closes the main window, the application is terminated """
        QWidget.close(self)



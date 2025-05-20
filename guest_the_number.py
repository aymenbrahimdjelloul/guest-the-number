#!/usr/bin/env python3

"""
@author : Aymen Brahim Djelloul
version : 1.0
date    : 20.05.2025
license : MIT

    \\ Guess The Number is a Python-based mind-reading game that mathematically
        guesses a number you're thinking of between 1 and 63.

"""

# IMPORTS
import os
import sys
from functools import partial
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QLabel,
                             QVBoxLayout, QHBoxLayout, QGridLayout,
                             QMainWindow, QFrame, QMessageBox, QStackedWidget)

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QFontDatabase, QColor, QPalette, QIcon


class NumberCard(QFrame):
    """Widget representing a card of numbers"""

    def __init__(self, numbers, colors, parent=None) -> None:
        super(NumberCard, self).__init__(parent)

        # Set frame styling
        self.setFrameShape(QFrame.StyledPanel)
        self.setLineWidth(2)
        self.setStyleSheet(f"""
            NumberCard {{
                background-color: {colors['card_background']};
                border: 3px solid {colors['primary']};
                border-radius: 10px;
            }}
        """)

        # Create grid layout for numbers
        grid = QGridLayout(self)
        grid.setSpacing(8)

        # Calculate optimal grid dimensions
        count: int = len(numbers)
        cols: int = min(8, count)  # Max 8 numbers per row

        # Add number labels to grid
        for i, num in enumerate(numbers):
            row, col = divmod(i, cols)
            label = QLabel(num)
            label.setAlignment(Qt.AlignCenter)
            label.setFont(QFont('Monospace', 16))
            label.setStyleSheet(f"""
                color: {colors['primary']};
                background-color: {colors['card_number_background']};
                border: 1px solid {colors['secondary']};
                border-radius: 5px;
                padding: 4px;
                min-width: 30px;
            """)
            grid.addWidget(label, row, col)


class GuessTheNumberGame(QMainWindow):
    """Main game window with improved GUI and game logic"""

    # Define card numbers
    CARDS_NUMS: list[list] = [
        list(map(str,
                 [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35, 37, 39, 41, 43, 45, 47, 49, 51, 53,
                  55, 57, 59, 61, 63])),
        list(map(str,
                 [2, 3, 6, 7, 10, 11, 14, 15, 18, 19, 22, 23, 26, 27, 30, 31, 34, 35, 38, 39, 42, 43, 46, 47, 50, 51,
                  54, 55, 58, 59, 62, 63])),
        list(map(str,
                 [4, 5, 6, 7, 12, 13, 14, 15, 20, 21, 22, 23, 28, 29, 30, 31, 36, 37, 38, 39, 44, 45, 46, 47, 52, 53,
                  54, 55, 60, 61, 62, 63])),
        list(map(str,
                 [8, 9, 10, 11, 12, 13, 14, 15, 24, 25, 26, 27, 28, 29, 30, 31, 40, 41, 42, 43, 44, 45, 46, 47, 56, 57,
                  58, 59, 60, 61, 62, 63])),
        list(map(str,
                 [16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 48, 49, 50, 51, 52, 53, 54, 55, 56,
                  57, 58, 59, 60, 61, 62, 63])),
        list(map(str,
                 [32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56,
                  57, 58, 59, 60, 61, 62, 63]))
    ]

    # Color scheme with more consistent naming
    COLORS: dict[str, str] = {
        'background': '#e0e0ff',
        'primary': '#7700ff',
        'secondary': '#a1aaff',
        'accent': '#154c79',
        'text': '#333333',
        'text_light': '#ffffff',
        'card_background': '#f0f0ff',
        'card_number_background': '#d8d8ff'
    }

    # Screen indices for stacked widget
    MAIN_MENU: int = 0
    INTRODUCTION: int = 1
    GAME: int = 2
    RESULT: int = 3

    def __init__(self) -> None:
        super(GuessTheNumberGame, self).__init__()

        # Initialize game state
        self.answer: str = ''
        self.card_num: int = 0

        # Set window icon from the first available ICO file
        base_dir: str = os.path.dirname(os.path.abspath(__file__))
        icon_locations: list[tuple[int, int]] = [
            os.path.join(base_dir, 'images', 'icon.ico'),
            os.path.join(base_dir, 'icon.ico'),

        ]

        # Set valid icon found
        for icon_path in icon_locations:
            if os.path.isfile(icon_path):
                self.setWindowIcon(QIcon(icon_path))
                break

        # Set window properties
        self.setWindowTitle('Guess The Number')
        self.setFixedSize(600, 500)

        # Create a central widget with a stacked layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Create stacked widget to manage different screens
        self.stacked_widget = QStackedWidget(self.central_widget)
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.addWidget(self.stacked_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Setup global appearance
        self.setup_appearance()

        # Initialize all screens
        self.init_screens()

        # Show main-menu initially
        self.stacked_widget.setCurrentIndex(self.MAIN_MENU)

    def setup_appearance(self) -> None:
        """Set up the global appearance of the app"""

        # Set color scheme
        palette: QPalette = QPalette()
        palette.setColor(QPalette.Window, QColor(self.COLORS['background']))
        palette.setColor(QPalette.WindowText, QColor(self.COLORS['text']))
        palette.setColor(QPalette.Button, QColor(self.COLORS['secondary']))
        palette.setColor(QPalette.ButtonText, QColor(self.COLORS['primary']))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

    def create_styled_button(self, text: str, onclick, width: int = 150, height: int = 50, font_size: int = 16) -> None:
        """Create a standardized styled button"""

        button = QPushButton(text)
        button.setFixedSize(width, height)
        button.setFont(QFont('Monospace', font_size))
        button.setCursor(Qt.PointingHandCursor)
        button.setStyleSheet(f"""
            QPushButton {{
                color: {self.COLORS["primary"]};
                border: 3px solid {self.COLORS["primary"]};
                border-radius: 10px;
                background-color: {self.COLORS["secondary"]};
                font-size: {font_size}pt;
                font-weight: bold;
            }}

            QPushButton:hover {{
                color: {self.COLORS["text_light"]};
                border-color: {self.COLORS["text_light"]};
                background-color: {self.COLORS["primary"]};
            }}
        """)
        button.clicked.connect(onclick)
        return button

    def init_screens(self) -> None:
        """Initialize all game screens"""

        # Main menu screen
        self.init_main_menu()

        # Introduction screen
        self.init_introduction_screen()

        # Game screen (will be updated during gameplay)
        self.game_screen = QWidget()
        self.stacked_widget.addWidget(self.game_screen)

        # Result screen (will be updated at the end)
        self.result_screen = QWidget()
        self.stacked_widget.addWidget(self.result_screen)

    def init_main_menu(self) -> None:
        """Initialize the main menu screen"""

        main_menu: QWidget = QWidget()
        layout = QVBoxLayout(main_menu)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        # Add logo
        logo = QLabel('Guess The Number')
        logo.setFont(QFont('Monospace', 32, QFont.Bold))
        logo.setStyleSheet(f'color: {self.COLORS["primary"]}')
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)

        # Add buttons
        button_layout = QVBoxLayout()
        button_layout.setSpacing(15)

        # Play button
        play_button = self.create_styled_button('PLAY', self.start_game)
        button_layout.addWidget(play_button, alignment=Qt.AlignCenter)

        # Exit button
        exit_button = self.create_styled_button('EXIT', self.close)
        button_layout.addWidget(exit_button, alignment=Qt.AlignCenter)

        layout.addLayout(button_layout)

        # Add credits at bottom
        credits = QLabel('Developed By Aymen Brahim Djelloul')
        credits.setStyleSheet(f'color: {self.COLORS["accent"]}')
        credits.setFont(QFont('Monospace', 10))
        credits.setAlignment(Qt.AlignCenter)
        layout.addWidget(credits)

        self.stacked_widget.addWidget(main_menu)

    def init_introduction_screen(self) -> None:
        """Initialize the introduction screen"""

        intro_screen: QWidget = QWidget()
        layout = QVBoxLayout(intro_screen)
        layout.setSpacing(20)

        # Header
        header = QLabel('How to Play', intro_screen)
        header.setFont(QFont('Monospace', 24, QFont.Bold))
        header.setStyleSheet(f'color: {self.COLORS["primary"]}')
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        # Instructions
        instructions = QLabel(
            "1. Think of a number between 1 and 63.\n\n"
            "2. Six cards will be shown one after another.\n\n"
            "3. For each card, tell me if your number is on it.\n\n"
            "4. At the end, I'll guess your number!", intro_screen
        )
        instructions.setFont(QFont('Monospace', 14))
        instructions.setStyleSheet(f'color: {self.COLORS["text"]}')
        instructions.setAlignment(Qt.AlignCenter)
        layout.addWidget(instructions)

        # Start button
        start_button = self.create_styled_button('Start', self.show_next_card, font_size=16)
        layout.addWidget(start_button, alignment=Qt.AlignCenter)

        self.stacked_widget.addWidget(intro_screen)

    def start_game(self) -> None:
        """Start a new game"""

        # Reset game state
        self.answers: str = ''
        self.card_num: int = 0

        # Show introduction screen
        self.stacked_widget.setCurrentIndex(self.INTRODUCTION)

    def update_game_screen(self) -> None:
        """Update the game screen with the current card"""

        # Create a new widget for the game screen
        game_widget: QWidget = QWidget()
        layout = QVBoxLayout(game_widget)
        layout.setSpacing(15)

        # Add card number indicator
        progress = QLabel(f"Card {self.card_num + 1} of 6")
        progress.setFont(QFont('Monospace', 12))
        progress.setStyleSheet(f'color: {self.COLORS["accent"]}')
        progress.setAlignment(Qt.AlignCenter)
        layout.addWidget(progress)

        # Add question
        question = QLabel("Is your number on this card?")
        question.setFont(QFont('Monospace', 16))
        question.setStyleSheet(f'color: {self.COLORS["primary"]}')
        question.setAlignment(Qt.AlignCenter)
        layout.addWidget(question)

        # Create number card
        card = NumberCard(self.CARDS_NUMS[self.card_num], self.COLORS)
        layout.addWidget(card)

        # Add yes/no buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)

        # Yes button
        yes_button = self.create_styled_button('Yes', partial(self.process_answer, '1'), width=100, height=40)
        button_layout.addWidget(yes_button)

        # No button
        no_button = self.create_styled_button('No', partial(self.process_answer, '0'), width=100, height=40)
        button_layout.addWidget(no_button)

        layout.addLayout(button_layout)

        # Replace the existing game screen with the new one
        old_widget = self.stacked_widget.widget(self.GAME)
        self.stacked_widget.removeWidget(old_widget)
        old_widget.deleteLater()

        self.stacked_widget.insertWidget(self.GAME, game_widget)
        self.stacked_widget.setCurrentIndex(self.GAME)

    def show_next_card(self) -> None:
        """Show the next card of numbers"""

        # Check if we have shown all cards
        if self.card_num >= 6:
            self.update_result_screen()
            self.stacked_widget.setCurrentIndex(self.RESULT)
            return

        # Update the game screen with current card
        self.update_game_screen()

    def process_answer(self, answer: int) -> None:
        """Process the user's answer"""

        # Add answer to binary string
        self.answers += answer
        self.card_num += 1

        # Show transition effect with proper timer
        self.centralWidget().setEnabled(False)
        QTimer.singleShot(50, self.show_next_card)
        QTimer.singleShot(50, lambda: self.centralWidget().setEnabled(True))

    def update_result_screen(self) -> None:
        """Update the result screen with calculated number"""

        # Create a new widget for the result screen
        result_widget = QWidget()
        layout = QVBoxLayout(result_widget)
        layout.setSpacing(30)

        # Add header
        header = QLabel('I know your number!')
        header.setFont(QFont("Monospace", 24, QFont.Bold))
        header.setStyleSheet(f'color: {self.COLORS["primary"]}')
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        # Calculate result
        result = self.get_result(self.answers)

        # Show result
        result_label = QLabel(result)
        result_label.setFont(QFont("Monospace", 72, QFont.Bold))
        result_label.setStyleSheet(f"""
            color: {self.COLORS["primary"]};
            background-color: {self.COLORS["secondary"]};
            border: 5px solid {self.COLORS["primary"]};
            border-radius: 20px;
            padding: 20px;
        """)
        result_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(result_label)

        # Add explanation
        explanation = QLabel("How did I do it? Each card represents a binary digit.\n"
                             "Your answers created a binary number that decoded to your choice!")
        explanation.setFont(QFont('Monospace', 12))
        explanation.setStyleSheet(f'color: {self.COLORS["accent"]}')
        explanation.setAlignment(Qt.AlignCenter)
        layout.addWidget(explanation)

        # Add buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)

        # Play again button
        play_again_button = self.create_styled_button('Play Again', self.start_game, width=180, height=50, font_size=14)
        button_layout.addWidget(play_again_button)

        # Main menu button
        menu_button = self.create_styled_button('Main Menu', self.go_to_main_menu, width=180, height=50, font_size=14)
        button_layout.addWidget(menu_button)

        layout.addLayout(button_layout)

        # Replace the existing result screen with the new one
        old_widget = self.stacked_widget.widget(self.RESULT)
        self.stacked_widget.removeWidget(old_widget)
        old_widget.deleteLater()

        self.stacked_widget.insertWidget(self.RESULT, result_widget)

    def go_to_main_menu(self) -> None:
        """Go back to the main menu"""
        self.stacked_widget.setCurrentIndex(self.MAIN_MENU)

    @staticmethod
    def get_result(binary_string) -> str:
        """Convert binary answer string to decimal"""
        # Reverse the binary string to match positional value
        binary_string = binary_string[::+1]

        # Calculate decimal value
        decimal: int = 0
        for i, bit in enumerate(binary_string):
            if bit == '1':
                decimal += 2 ** i

        return str(decimal)


def main() -> None:
    """Main application entry point"""

    app: QApplication = QApplication(sys.argv)

    # Set application-wide default monospace font
    app.setFont(QFont("Monospace"))

    try:
        window: GuessTheNumberGame = GuessTheNumberGame()
        window.show()
        sys.exit(app.exec_())

    except Exception as e:
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setText("An error occurred")
        error_dialog.setInformativeText(str(e))
        error_dialog.setWindowTitle("Error")
        error_dialog.exec_()
        sys.exit(1)


if __name__ == "__main__":
    main()

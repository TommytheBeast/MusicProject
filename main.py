import sys
import random
import csv
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QMessageBox, QVBoxLayout
from PyQt5.QtCore import Qt, QTimer

# Initial function for validating the user
def authenticate(username, password):
    # Compare the entered credentials to the pairs in the file
    with open("credentials.txt", "r") as file:
        for line in file:
            valid_username, valid_password = line.strip().split(":")
            if username == valid_username and password == valid_password:
                return True
    return False

# Function to choose a random song from the CSV file
def select_song():
    # Read the songs from the CSV file
    with open("songs.csv", "r") as file:
        reader = csv.reader(file)
        songs = list(reader)
        
    # Select a random song
    if songs:
        selected_song = random.choice(songs)
        return selected_song
    else:
        return None

# Secondary function to handle login button click event
def login():
    global selected_song  # Declare selected_song as a global variable

    # Retrieve the entered username and password
    username = username_input.text()
    password = password_input.text()

    # Authenticate user
    if authenticate(username, password):
        selected_song = select_song()
        if selected_song:
            QMessageBox.information(window, "Authentication", f"Authentication successful!\n\nSelected Song: {selected_song[2]}")

            # Show artist name and song initials in the GUI
            artist_label.setText(f"Artist: {selected_song[0]}")
            song_initials_label.setText(f"Song Initials: {selected_song[1]}")

            # Remove authentication widgets from the screen
            layout.removeWidget(username_label)
            layout.removeWidget(username_input)
            layout.removeWidget(password_label)
            layout.removeWidget(password_input)
            layout.removeWidget(login_button)
            username_label.deleteLater()
            password_label.deleteLater()
            login_button.deleteLater()

            # Enable the guessing widget and guess button
            song_guess_label.show()
            song_guess_input.show()
            guess_button.setEnabled(True)
            score_label.show()

            # Start the timer for song duration
            timer.start(30000)  # 30 seconds

        else:
            QMessageBox.warning(window, "Authentication", "Authentication failed. Invalid username or password.")
            # Handle authentication failure appropriately (e.g., show an error message)
    else:
        QMessageBox.warning(window, "Authentication", "Authentication failed. Invalid username or password.")
        # Handle authentication failure appropriately (e.g., show an error message)

# Function to handle guess button click event
def guess():
    global selected_song  # Declare selected_song as a global variable

    # Retrieve the entered guess for the song name
    song_guess = song_guess_input.text()

    # Retrieve the correct song name from the selected song
    full_song_name = selected_song[2]

    # Compare the user's guess with the correct answer
    if song_guess.lower() == full_song_name.lower():
        score = 3
        message = "Correct guess! You earned 3 points."
    else:
        score = 0
        message = "Incorrect guess! No points earned."
        # Decrease the player's life count
        global player_lives
        player_lives -= 1
        lives_label.setText(f"Lives: {player_lives}")
        # Check if the player has lost all lives
        if player_lives == 0:
            end_game()

    # Update the player's score
    global player_score
    player_score += score
    score_label.setText(f"Score: {player_score} points")

    # Show the result message in a message box
    QMessageBox.information(window, "Guess Result", message)

    # Clear the guess input field
    song_guess_input.clear()

    # Select a new song for the next round
    selected_song = select_song()
    if selected_song:
        # Update the artist name and song initials in the GUI
        artist_label.setText(f"Artist: {selected_song[0]}")
        song_initials_label.setText(f"Song Initials: {selected_song[1]}")

        # Restart the timer for the new song duration
        timer.start(30000)  # 30 seconds
    else:
        end_game()

# Function to end the game and show the final score
def end_game():
    # Save the player's score in the leaderboard file
    with open("leaderboard.txt", "a") as file:
        file.write(f"{username_input.text()}:{player_score}\n")

    # Load the leaderboard scores from the file
    leaderboard_scores = []
    with open("leaderboard.txt", "r") as file:
        for line in file:
            line = line.strip()
            if line:
                parts = line.split(":")
                if len(parts) == 2:
                    username, score = parts
                    leaderboard_scores.append((username, int(score)))

    # Sort the leaderboard scores in descending order
    leaderboard_scores.sort(key=lambda x: x[1], reverse=True)

    # Prepare the leaderboard message
    leaderboard_message = "Leaderboard:\n\n"
    for i, (username, score) in enumerate(leaderboard_scores[:5]):
        leaderboard_message += f"{i+1}. {username}: {score} points\n"
    leaderboard_message += "\nYour Score: {} points".format(player_score)

    # Show the leaderboard in a message box
    QMessageBox.information(window, "Game Over", leaderboard_message)
    # Close the application
    app.quit()


# Create the GUI window
app = QApplication(sys.argv)
window = QWidget()
window.setWindowTitle("User Authentication")

# Create username label and input field
username_label = QLabel(window)
username_label.setText("Username:")
username_input = QLineEdit(window)

# Create password label and input field
password_label = QLabel(window)
password_label.setText("Password:")
password_input = QLineEdit(window)
password_input.setEchoMode(QLineEdit.Password)

# Create login button
login_button = QPushButton(window)
login_button.setText("Login")
login_button.clicked.connect(login)

# Create layout for the widgets
layout = QVBoxLayout()
layout.addWidget(username_label)
layout.addWidget(username_input)
layout.addWidget(password_label)
layout.addWidget(password_input)
layout.addWidget(login_button)

# Set the window layout
window.setLayout(layout)

# Show the GUI window
window.show()

# Create labels and input fields for song guessing
song_guess_label = QLabel(window)
song_guess_label.setText("Guess the Song:")
song_guess_input = QLineEdit(window)

# Create guess button
guess_button = QPushButton(window)
guess_button.setText("Guess")
guess_button.clicked.connect(guess)
guess_button.setEnabled(False)

# Create label for displaying the artist name
artist_label = QLabel(window)

# Create label for displaying the song initials
song_initials_label = QLabel(window)

# Create layout for the guess widgets
guess_layout = QVBoxLayout()
guess_layout.addWidget(song_guess_label)
guess_layout.addWidget(song_guess_input)
guess_layout.addWidget(guess_button)
guess_layout.addWidget(artist_label)
guess_layout.addWidget(song_initials_label)

# Connect the layout for guess widgets to the main layout
layout.addLayout(guess_layout)

# Create a timer for the song duration
timer = QTimer()
timer.setSingleShot(True)
timer.timeout.connect(end_game)

# Initialize player's score and lives
player_score = 0
player_lives = 3

# Create label for displaying the player's score
score_label = QLabel(window)
score_label.setText("Score: 0 points")
layout.addWidget(score_label)

# Create label for displaying the remaining lives
lives_label = QLabel(window)
lives_label.setText("Lives: 3")
layout.addWidget(lives_label)

# Start the application event loop
sys.exit(app.exec_())

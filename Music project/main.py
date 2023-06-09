import sys
import random
import os
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QMessageBox, QVBoxLayout
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl, QTimer

# Initial function for validating the user
def authenticate(username, password):
    # Compare the entered credentials to external file
    with open("credentials.txt", "r") as file:
        valid_username = file.readline().strip()
        valid_password = file.readline().strip()

    if username == valid_username and password == valid_password:
        return True
    else:
        return False

# Function designed to choose a song randomly from a folder
def select_song():
    # Find the path to the songs folder
    folder_path = "songs/"

    # Retrieve the list of song files in the folder
    song_files = os.listdir(folder_path)
    song_files = [file for file in song_files if file.endswith(".mp3")]

    # Selects the song randomly
    if song_files:
        selected_song = random.choice(song_files)
        return selected_song
    else:
        return None

# Secondary function to handle login button click event
def login():
    # Retrieve the entered username and password
    username = username_input.text()
    password = password_input.text()

    # Authenticate user
    if authenticate(username, password):
        selected_song = select_song()
        if selected_song:
            QMessageBox.information(window, "Authentication", f"Authentication successful!\n\nSelected Song: {selected_song}")

            # Play the selected song
            song_path = os.path.join("songs", selected_song)
            media_content = QMediaContent(QUrl.fromLocalFile(song_path))
            song_player.setMedia(media_content)
            song_player.play()

            # Retrieve initials of the artist from the selected song
            artist_initials = selected_song.split("_")[0].upper()

            # Show initials of the artist in the GUI
            artist_initials_label.setText(f"Artist Initials: {artist_initials}")

            # Remove authentication widget from the screen
            layout.removeWidget(username_label)
            layout.removeWidget(username_input)
            layout.removeWidget(password_label)
            layout.removeWidget(password_input)
            layout.removeWidget(login_button)
            username_label.deleteLater()
            username_input.deleteLater()
            password_label.deleteLater()
            password_input.deleteLater()
            login_button.deleteLater()

            # Enable the guessing widget and guess button
            song_guess_label.show()
            song_guess_input.show()
            artist_guess_label.show()
            artist_guess_input.show()
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
    # Retrieve the entered guess for song name and artist
    song_guess = song_guess_input.text()
    artist_guess = artist_guess_input.text()

    # Retrieve the correct song name and artist from the selected song
    song_name = " ".join(selected_song.split("_")[2:]).replace(".mp3", "")
    artist_name = selected_song.split("_")[1]

    # Compare the user's guesses with the correct answers
    if song_guess.lower() == song_name.lower() and artist_guess.lower() == artist_name.lower():
        score = 3
        message = "Correct guess! You earned 3 points."
    elif song_guess.lower() == song_name.lower() or artist_guess.lower() == artist_name.lower():
        score = 1
        message = "Partial guess! You earned 1 point."
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

    # Clear the guess input fields
    song_guess_input.clear()
    artist_guess_input.clear()

    # Select a new song for the next round
    selected_song = select_song()
    if selected_song:
        # Update the initials of the artist for the new song
        artist_initials = selected_song.split("_")[0].upper()
        artist_initials_label.setText(f"Artist Initials: {artist_initials}")
        # Play the new song
        song_path = os.path.join("songs", selected_song)
        media_content = QMediaContent(QUrl.fromLocalFile(song_path))
        song_player.setMedia(media_content)
        song_player.play()
        # Restart the timer for the new song duration
        timer.start(30000)  # 30 seconds
    else:
        end_game()

# Function to end the game and show the leaderboard
def end_game():
    # Stop the song player
    song_player.stop()

    # Save the player's score in the leaderboard file
    with open("leaderboard.txt", "a") as file:
        file.write(f"{username_input.text()}:{player_score}\n")

    # Load the leaderboard scores from the file
    leaderboard_scores = []
    with open("leaderboard.txt", "r") as file:
        for line in file:
            line = line.strip()
            if line:
                username, score = line.split(":")
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

# Create artist initials label
artist_initials_label = QLabel(window)
artist_initials_label.hide()  # Hide the artist initials label initially

# Create song name and artist guess labels and input fields
song_guess_label = QLabel(window)
song_guess_label.setText("Guess Song Name:")
song_guess_input = QLineEdit(window)
song_guess_input.hide()  # Hide the song guess input field initially
artist_guess_label = QLabel(window)
artist_guess_label.setText("Guess Artist Name:")
artist_guess_input = QLineEdit(window)
artist_guess_input.hide()  # Hide the artist guess input field initially

# Create guess button
guess_button = QPushButton(window)
guess_button.setText("Guess")
guess_button.clicked.connect(guess)
guess_button.setEnabled(False)  # Disable the guess button initially

# Create score and lives labels
score_label = QLabel(window)
score_label.setText("Score: 0 points")
score_label.hide()  # Hide the score label initially
lives_label = QLabel(window)
lives_label.setText("Lives: 3")
lives_label.hide()  # Hide the lives label initially

# Create layout for the window
layout = QVBoxLayout()
layout.addWidget(username_label)
layout.addWidget(username_input)
layout.addWidget(password_label)
layout.addWidget(password_input)
layout.addWidget(login_button)
layout.addWidget(artist_initials_label)
layout.addWidget(song_guess_label)
layout.addWidget(song_guess_input)
layout.addWidget(artist_guess_label)
layout.addWidget(artist_guess_input)
layout.addWidget(guess_button)
layout.addWidget(score_label)
layout.addWidget(lives_label)

window.setLayout(layout)
window.show()

# Create a media player for playing songs
song_player = QMediaPlayer()

# Initialize variables
selected_song = None
player_score = 0
player_lives = 3

# Create a timer for song duration
timer = QTimer()

# Connect the timer's timeout signal to the guess function
timer.timeout.connect(guess)

# Start the GUI event loop
sys.exit(app.exec_())

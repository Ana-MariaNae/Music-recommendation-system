function interact(song_id, action) {
    console.log(action);
    fetch("/interact", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ user_id: user_id, song_id: song_id, action: action })
    });
}

function sendSetViewPortion(songId, portion) {
    fetch(`/set_view_portion`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ user_id, song_id: songId, portion }),
    });
}

// Progress Bar with Pause Button
function startProgress(songId, duration = 60) {
    const progressBar = document.getElementById(`progress-bar-${songId}`);
    const playButton = document.getElementById(`play-button-${songId}`);
    const pauseButton = document.getElementById(`pause-button-${songId}`);

    let currentProgress = 0;
    const interval = setInterval(() => {
        if (currentProgress >= duration) {
            clearInterval(interval);
            return;
        }

        progressBar.style.width = `${(currentProgress / duration) * 100}%`;
        currentProgress++;
    }, 1000);

    // Pause Functionality
    pauseButton.addEventListener('click', () => {
        clearInterval(interval);
    });

    // Stop and play a new song if necessary
    playButton.addEventListener('click', () => {
        clearInterval(interval);
        stopSong(songId, currentProgress / duration);
    });
}

// Enforce Exactly 3 Checkboxes
document.getElementById("genre-form")?.addEventListener("submit", (event) => {
    console.log(event);
    const checkboxes = document.querySelectorAll("input[type='checkbox']:checked");
    console.log(checkboxes);
    console.log(checkboxes?.length);
    if (checkboxes?.length !== 3) {
        alert("Please select exactly 3 genres.");
        event.preventDefault();
    }
});

var currentSongId = null;
var progressInterval = null;

function playSong(songId) {
    // Stop the currently playing song
    if (currentSongId && currentSongId !== songId) {
        stopSong(currentSongId);
    }

    currentSongId = songId;

    // Update the global progress bar
    document.getElementById("global-progress-container").style.display = "block";
    document.getElementById("current-song-title").innerText = document.querySelector(`#song-${songId} h3`).innerText;

    const progressBar = document.getElementById("global-progress-bar");
    let progress = 0;
    progressBar.style.width = "0%";

    progressInterval = setInterval(() => {
        progress += 1;
        progressBar.style.width = `${progress}%`;

        if (progress >= 100) {
            clearInterval(progressInterval);
            sendSetViewPortion(songId, 1); // Song completed
        }
    }, 600); // 1 minute simulated as 60 seconds
}

function stopSong(songId) {
    if (songId === currentSongId) {
        clearInterval(progressInterval);
        sendSetViewPortion(songId, parseFloat(document.getElementById("global-progress-bar").style.width) / 100);
        document.getElementById("global-progress-container").style.display = "none";
        currentSongId = null;
    }
}

function createUser() {
    const userId = document.getElementById("user_id").value;
    const name = document.getElementById("name").value;
    const gender = document.getElementById("gender").value;
    const birthday = document.getElementById("birthday").value;
    console.log(birthday);
    const genres = Array.from(document.querySelectorAll("input[name='genre']:checked")).map(
        (checkbox) => checkbox.value
    );
    console.log(genres);
    console.log(JSON.stringify({ user_id: userId, name, gender, birthday, genres }));

    fetch("/create_account", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ user_id: userId, name, gender, birthday, genres }),
    }).then((response) => {
        console.log(response);
        if (response.ok) {
            window.location.href = `/recommendations/${user_id}`;
        } else {
            alert("Error creating user!");
        }
    });
}

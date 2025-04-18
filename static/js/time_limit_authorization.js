var countdownElement = document.getElementById('countdown');
var countdownTime = 5;

function updateCountdown() {
    countdownElement.textContent = countdownTime;
    countdownTime--;
    if (countdownTime < 0) {
        window.location.href = "/home"; // Замените на нужный URL
    }
}

setInterval(updateCountdown, 1000);

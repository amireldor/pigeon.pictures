window.addEventListener('load', () => {
    const countdown = document.getElementById("countdown")
    new Countdown(countdown)
})

function Countdown(element) {
    const countdownEnd = nextUpdateTime; // rendered from backend :)
    tick()

    function tick() {
        const ended = action()
        if (ended) {
            element.innerText += " -- refresh, for glory!"
            element.classList.toggle("ended")
        } else {
            setTimeout(tick, 1000)
        }
    }

    function action() {
        const timeLeft = calculateTimeLeft()
        const ended = timeLeft <= 0
        if (ended) {
            element.innerText = formatTimeLeft(0)
        } else {
            element.innerText = formatTimeLeft(timeLeft)
        }
        return ended
    }

    function calculateTimeLeft() {
        return Math.max(0, countdownEnd - Date.now())
    }

    function formatTimeLeft(timeLeft) {
        const minutes = parseInt(timeLeft / (60 * 1000))
        const seconds = parseInt((timeLeft / 1000) % 60)
        const zeroPad = seconds < 10 ? "0" : ""
        return `${minutes}:${zeroPad}${seconds}`
    }
}

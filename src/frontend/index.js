window.addEventListener('load', () => {
    const countdown = document.getElementById("countdown")
    new Countdown(countdown)
})

function Countdown(element) {
    const countdownEnd = Date.now() + calculateSecondsToCountdownEnd() * 1000
    tick()

    function calculateSecondsToCountdownEnd() {
        const secondsInCycle = 30 * 60
        const date = new Date()
        const nowSeconds = date.getSeconds() + 60 * date.getMinutes()
        const nowSecondsMod = nowSeconds % secondsInCycle
        const secondsToEnd = secondsInCycle - nowSecondsMod
        return secondsToEnd
    }

    function tick() {
        action()
        requestAnimationFrame(tick)
    }

    function action() {
        const timeLeft = calculateTimeLeft()
        element.innerText = formatTimeLeft(timeLeft)
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
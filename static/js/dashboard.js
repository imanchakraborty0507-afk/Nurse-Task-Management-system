/**
 * Dashboard Live Clock & Dynamic Metric Updates
 */

document.addEventListener("DOMContentLoaded", function () {
  // Live Clock updater
  const liveClockEl = document.getElementById("liveClock");
  if (liveClockEl) {
    function updateClock() {
      const now = new Date();
      liveClockEl.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    }
    updateClock();
    setInterval(updateClock, 1000);
  }
});

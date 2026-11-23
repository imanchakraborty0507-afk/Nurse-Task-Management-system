/**
 * Notification Real-time Poller & Reader
 */

async function markNotificationRead(notifId) {
  try {
    const res = await fetch(`/api/notifications/${notifId}/read`, { method: "POST" });
    const data = await res.json();
    if (data.success) {
      const el = document.getElementById(`notif-item-${notifId}`);
      if (el) {
        el.classList.remove("unread", "bg-light");
      }
      updateNotificationBadge();
    }
  } catch (err) {
    console.error("Failed to mark notification read:", err);
  }
}

async function markAllNotificationsRead() {
  try {
    const res = await fetch("/api/notifications/mark-all-read", { method: "POST" });
    const data = await res.json();
    if (data.success) {
      window.location.reload();
    }
  } catch (err) {
    console.error("Failed to mark all read:", err);
  }
}

async function updateNotificationBadge() {
  try {
    const res = await fetch("/api/notifications/unread-count");
    const data = await res.json();
    if (data.success) {
      const badge = document.getElementById("notifBadgeCount");
      if (badge) {
        if (data.count > 0) {
          badge.textContent = data.count;
          badge.style.display = "inline-block";
        } else {
          badge.style.display = "none";
        }
      }
    }
  } catch (e) {
    // Ignore polling errors
  }
}

// Poll every 30 seconds
document.addEventListener("DOMContentLoaded", function () {
  setInterval(updateNotificationBadge, 30000);
});

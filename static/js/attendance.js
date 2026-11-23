/**
 * Attendance Interactive AJAX Handler
 * Supports one-click Check-In and Check-Out with immediate visual updates.
 */

async function ajaxCheckIn() {
  try {
    const res = await fetch('/api/attendance/check-in', { method: 'POST' });
    const data = await res.json();
    if (data.success) {
      window.location.reload();
    } else {
      alert("Check-In Error: " + data.error);
    }
  } catch (err) {
    alert("Network error during check-in.");
  }
}

async function ajaxCheckOut() {
  if (!confirm("Are you sure you want to Check Out for today?")) return;
  try {
    const res = await fetch('/api/attendance/check-out', { method: 'POST' });
    const data = await res.json();
    if (data.success) {
      window.location.reload();
    } else {
      alert("Check-Out Error: " + data.error);
    }
  } catch (err) {
    alert("Network error during check-out.");
  }
}

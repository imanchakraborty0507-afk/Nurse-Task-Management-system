/**
 * Task Management Interactive Handler
 * Enables AJAX status updates, audit history loading, and instant feedback.
 */

async function updateTaskStatusAjax(taskId, newStatus, comment = "") {
  try {
    const res = await fetch(`/api/tasks/${taskId}/status`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: newStatus, comment: comment })
    });
    const data = await res.json();
    if (data.success) {
      window.location.reload();
    } else {
      alert("Error: " + data.error);
    }
  } catch (err) {
    console.error("Failed to update status:", err);
    alert("Network error updating task status.");
  }
}

async function loadTaskDetailsModal(taskId) {
  const modalBody = document.getElementById("taskModalBody");
  if (!modalBody) return;

  modalBody.innerHTML = `
    <div class="text-center py-4">
      <div class="spinner-border text-primary" role="status"></div>
      <p class="text-muted mt-2">Loading task details...</p>
    </div>
  `;

  try {
    const res = await fetch(`/api/tasks/${taskId}`);
    const data = await res.json();
    if (data.success) {
      const t = data.task;
      modalBody.innerHTML = `
        <div class="mb-3">
          <span class="badge ${t.priority === 'CRITICAL' ? 'badge-priority-critical' : 'badge-priority-high'} me-2">${t.priority}</span>
          <span class="badge badge-status-${t.status.toLowerCase().replace('_', '-')}">${t.status}</span>
        </div>
        <h5>${t.task_title}</h5>
        <p class="text-muted">${t.description}</p>
        <hr/>
        <div class="row g-2 text-sm mb-3">
          <div class="col-6"><strong>Patient:</strong> ${t.patient_name} (${t.room_number || 'Ward ' + t.ward_name})</div>
          <div class="col-6"><strong>Nurse:</strong> ${t.nurse_name}</div>
          <div class="col-6"><strong>Due Time:</strong> ${t.due_time}</div>
          <div class="col-6"><strong>Assigned By:</strong> ${t.assigned_by_name}</div>
        </div>
        ${t.notes ? `<div class="p-2 bg-light rounded mb-3"><strong>Notes:</strong><pre class="m-0" style="white-space: pre-wrap; font-family: inherit;">${t.notes}</pre></div>` : ''}
      `;
    }
  } catch (err) {
    modalBody.innerHTML = `<div class="alert alert-danger">Failed to load task details.</div>`;
  }
}

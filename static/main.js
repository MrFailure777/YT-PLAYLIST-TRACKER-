document.addEventListener('DOMContentLoaded', () => {
  // === Theme toggle ===
  const themeToggle = document.getElementById('theme-toggle');
  const body = document.body;
  const savedTheme = localStorage.getItem('pt_theme');

  if (savedTheme === 'light') body.classList.add('light');

  themeToggle?.addEventListener('click', () => {
    body.classList.toggle('light');
    localStorage.setItem('pt_theme', body.classList.contains('light') ? 'light' : 'dark');
  });

  // === Playlist progress buttons ===
  const handleUpdate = async (id, action) => {
    const res = await fetch(`/playlist/${id}/${action}`, { method: 'POST' });
    if (res.ok) {
      const data = await res.json();
      updateCard(id, data.percent, data.completed);
    } else {
      alert(`Failed to ${action} playlist progress`);
    }
  };

  document.querySelectorAll('.inc').forEach(btn => {
    btn.addEventListener('click', () => handleUpdate(btn.dataset.id, 'increment'));
  });

  document.querySelectorAll('.dec').forEach(btn => {
    btn.addEventListener('click', () => handleUpdate(btn.dataset.id, 'decrement'));
  });

  document.querySelectorAll('.remove-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      if (!confirm('Remove this playlist?')) return;
      const id = btn.dataset.id;
      const res = await fetch(`/playlist/${id}/remove`, { method: 'POST' });
      if (res.ok) {
        document.getElementById('pl-' + id)?.remove();
        window.location.reload(); // ensures totals update
      } else {
        alert('Could not remove playlist');
      }
    });
  });

  // === Modal handling ===
  const modals = document.querySelectorAll('.modal');
  const openButtons = document.querySelectorAll('[data-modal]');
  const closeButtons = document.querySelectorAll('.close-btn');

  openButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const target = document.getElementById(btn.dataset.modal);
      target?.classList.add('active');
    });
  });

  closeButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      btn.closest('.modal')?.classList.remove('active');
    });
  });

  modals.forEach(modal => {
    modal.addEventListener('click', e => {
      if (e.target === modal) modal.classList.remove('active');
    });
  });
});

// === Update playlist card ===
function updateCard(id, percent, completed) {
  const el = document.getElementById('pl-' + id);
  if (!el) return;

  const fill = el.querySelector('.bar-fill');
  const info = el.querySelector('.progress-info');

  if (fill) fill.style.width = percent + '%';
  if (info) {
    info.textContent = `${completed} / ? videos — ${percent}%`;
  }

  // Quick reload to refresh totals (simple but effective)
  window.location.reload();
}


// CANVAS

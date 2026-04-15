async function fetchJSON(url, options = {}) {
  const res = await fetch(url, options);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

function renderNoteCard(n) {
  const div = document.createElement('div');
  div.className = 'note-card';
  div.innerHTML = `
    <div class="note-header">
      <strong>${n.title}</strong>
      <span class="note-id">${n.id}</span>
    </div>
    <div class="note-meta">${n.notebook ?? ''} • ${n.updated_at}</div>
    <div class="note-content">${n.content}</div>
    <div class="note-tags">${(n.tags || []).join(', ')}</div>
    <button data-id="${n.id}" class="delete-btn">Eliminar</button>
  `;
  return div;
}

async function loadNotes() {
  const notebook = document.getElementById('notebookFilter').value;
  const tag = document.getElementById('tagFilter').value;
  const url = new URL('/notes', window.location.origin);
  if (notebook) url.searchParams.append('notebook', notebook);
  if (tag) url.searchParams.append('tag', tag);
  const notes = await fetchJSON(url.toString());
  const list = document.getElementById('notesList');
  list.innerHTML = '';
  for (const n of notes) {
    list.appendChild(renderNoteCard(n));
  }
  // Bind delete buttons
  document.querySelectorAll('.delete-btn').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      const id = e.currentTarget.getAttribute('data-id');
      await fetchJSON(`/notes/${id}`, { method: 'DELETE' }).catch(() => {});
      await loadNotes();
    });
  });
}

async function loadNotebooks() {
  const data = await fetchJSON('/notebooks');
  const select = document.getElementById('notebookFilter');
  select.innerHTML = '<option value="">Todos</option>';
  data.forEach(nb => {
    const opt = document.createElement('option');
    opt.value = nb;
    opt.textContent = nb;
    select.appendChild(opt);
  });
}

async function addNoteFromForm(e) {
  e.preventDefault();
  const title = document.getElementById('title').value.trim();
  const content = document.getElementById('content').value.trim();
  const notebook = document.getElementById('notebook').value.trim() || null;
  const tagsRaw = document.getElementById('tags').value.trim();
  const tags = tagsRaw ? tagsRaw.split(',').map(t => t.trim()).filter(t => t) : [];
  if (!title || !content) return;
  await fetch('/notes', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, content, notebook, tags })
  }).catch(() => {});
  document.getElementById('noteForm').reset();
  await loadNotebooks();
  await loadNotes();
}

document.addEventListener('DOMContentLoaded', async () => {
  // Build UI
  if (typeof window === 'undefined') return;
  document.getElementById('noteForm').addEventListener('submit', addNoteFromForm);
  await loadNotebooks();
  await loadNotes();
  document.getElementById('applyFilters').addEventListener('click', loadNotes);
});

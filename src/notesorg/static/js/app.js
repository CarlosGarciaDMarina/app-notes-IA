const DEBUG_UI = true;
async function fetchJSON(url, options = {}) {
  const res = await fetch(url, options);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const ct = res.headers.get('content-type') || '';
  if (ct.includes('application/json')) return res.json();
  return res.text();
}

function formatDate(iso) {
  try {
    const d = new Date(iso);
    const day = String(d.getDate()).padStart(2, '0');
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const year = d.getFullYear();
    return `${day}/${month}/${year}`;
  } catch (e) {
    return iso;
  }
}

function renderNoteCard(n) {
  const div = document.createElement('div');
  div.className = 'note-card';
  // Attach data attributes to enable modal content without extra fetch
  div.dataset.title = n.title;
  div.dataset.content = n.content;
  div.dataset.notebook = n.notebook || '';
  div.dataset.tags = JSON.stringify(n.tags || []);
  div.dataset.updated_at = n.updated_at;
  div.dataset.created_at = n.created_at;
  div.dataset.id = n.id;
  div.innerHTML = `
    <div class="note-header">
      <span class="note-title">${n.title}</span>
      <span class="note-date">${formatDate(n.updated_at)}</span>
    </div>
  `;
  div.addEventListener('click', () => {
    openNoteModal({
      id: n.id,
      title: n.title,
      content: n.content,
      notebook: n.notebook,
      tags: n.tags,
      updated_at: n.updated_at,
      created_at: n.created_at
    });
  });
  return div;
}

function escapeHtml(str) {
  if (str == null) return '';
  return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

// Snackbar utility to show messages and optional actions
function showSnackbar(message, actions) {
  const sn = document.getElementById('snackbar');
  if (!sn) return;
  let inner = `<span>${escapeHtml(message)}</span>`;
  if (actions && actions.length) {
    inner += '<span class="snackbar-actions">';
    actions.forEach((a, i) => {
      inner += `<button class="snackbar-btn" data-index="${i}">${a.label}</button>`;
    });
    inner += '</span>';
  }
  sn.innerHTML = inner;
  // Wire up actions
  if (actions && actions.length) {
    sn.querySelectorAll('.snackbar-btn').forEach((btn, idx) => {
      btn.addEventListener('click', () => {
        actions[idx].onClick?.();
        hideSnackbar();
      });
    });
  }
  sn.classList.add('show');
  if (showSnackbar._t) clearTimeout(showSnackbar._t);
  showSnackbar._t = setTimeout(() => { sn.classList.remove('show'); }, 4000);
}

function hideSnackbar() {
  const sn = document.getElementById('snackbar');
  if (sn) sn.classList.remove('show');
}

function openNoteModal(note) {
  const modal = document.getElementById('noteModal');
  if (!modal) return;
  document.getElementById('modalTitle').textContent = note.title;
  const body = document.getElementById('modalBody');
  const tags = (note.tags && note.tags.length) ? note.tags.join(', ') : '';
  body.innerHTML = `
    <div id="modalStatus" class="modal-status" style="color:#f87171; display:none; padding:6px 0;"></div>
    <form id="noteEditForm" data-id="${escapeHtml(note.id)}">
      <div class="field">
        <label for="edit_title">Título</label>
        <input id="edit_title" value="${escapeHtml(note.title)}" />
      </div>
      <div class="field">
        <label for="edit_content">Contenido</label>
        <textarea id="edit_content" rows="6">${escapeHtml(note.content)}</textarea>
      </div>
      <div class="field">
        <label for="edit_notebook">Cuaderno</label>
        <input id="edit_notebook" value="${escapeHtml(note.notebook || '')}" />
      </div>
      <div class="field">
        <label for="edit_tags">Etiquetas</label>
        <input id="edit_tags" value="${escapeHtml(tags)}" />
      </div>
      <div class="field" style="margin-top:6px;">
        <label>Creado</label>
        <input id="edit_created" value="${formatDate(note.created_at)}" readonly />
      </div>
      <div class="field">
        <label>Actualizado</label>
        <input id="edit_updated" value="${formatDate(note.updated_at)}" readonly />
      </div>
    </form>
  `;
  modal.style.display = 'flex';
  // Close handler
  const closeBtn = document.getElementById('modalClose');
  const onClose = () => { modal.style.display = 'none'; closeBtn.removeEventListener('click', onClose); };
  closeBtn.addEventListener('click', onClose);

  // Save handler
  document.getElementById('modalSave').onclick = async () => {
    const id = note.id;
    const titleEd = document.getElementById('edit_title').value.trim();
    const contentEd = document.getElementById('edit_content').value;
    const notebookEd = document.getElementById('edit_notebook').value;
    const tagsEd = document.getElementById('edit_tags').value;
    const tagsArr = tagsEd ? tagsEd.split(',').map(t => t.trim()).filter(t => t) : [];
    const res = await fetch(`/notes/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title: titleEd, content: contentEd, notebook: notebookEd, tags: tagsArr })
    }).catch(() => {});
    if (res && res.ok) {
      // Close immediately for better UX
      modal.style.display = 'none';
      // Reload in background and await to ensure UI updates
      await Promise.all([loadNotebooks(), loadNotes()]);
      const statusEl = document.getElementById('modalStatus');
      if (statusEl) { statusEl.style.display = 'none'; statusEl.textContent = ''; }
    } else {
      let errorMsg = 'Error al guardar';
      try {
        const data = await (res && res.json ? res.json() : Promise.resolve(null));
        if (data && data.error) errorMsg = data.error;
      } catch { /* ignore */ }
      try {
        const t = await (res && res.text ? res.text() : Promise.resolve(null));
        if (t) errorMsg = t;
      } catch { /* ignore */ }
      if (typeof alert === 'function' && DEBUG_UI) {
        alert(errorMsg);
      } else {
        showSnackbar(errorMsg);
      }
    }
  };

  // Delete handler - delegate to a dedicated confirm modal
  const deleteBtn = document.getElementById('modalDelete');
  if (deleteBtn) {
    deleteBtn.onclick = () => {
      openDeleteConfirm(note, async () => {
        await fetch(`/notes/${note.id}`, { method: 'DELETE' }).catch(() => {});
        modal.style.display = 'none';
        await loadNotebooks();
        await loadNotes();
      });
    };
  }
}

function openDeleteConfirm(note, onConfirm) {
  const modal = document.getElementById('confirmModal');
  const title = document.getElementById('confirmTitle');
  const body = document.getElementById('confirmBody');
  if (!modal || !title || !body) {
    if (confirm) {
      if (confirm('¿Desea eliminar esta nota?')) onConfirm?.();
    }
    return;
  }
  title.textContent = 'Confirmación';
  body.textContent = '¿Desea eliminar esta nota?';
  modal.style.display = 'flex';
  const ok = document.getElementById('confirmOk');
  const cancel = document.getElementById('confirmCancel');
  const onOk = () => { modal.style.display = 'none'; ok.removeEventListener('click', onOk); cancel.removeEventListener('click', onCancel); onConfirm?.(); };
  const onCancel = () => { modal.style.display = 'none'; ok.removeEventListener('click', onOk); cancel.removeEventListener('click', onCancel); };
  ok.addEventListener('click', onOk);
  cancel.addEventListener('click', onCancel);
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
  // No delete button in UI yet (preview mode)
}

async function loadNotebooks() {
  const data = await fetchJSON('/notebooks');
  const select = document.getElementById('notebookFilter');
  // Normalize potential shapes: string or { name: string }
  let notebooks = data || [];
  if (notebooks.length > 0 && typeof notebooks[0] === 'object' && 'name' in notebooks[0]) {
    notebooks = notebooks.map(n => n.name || '');
  }
  // Deduplicate and remove empties
  const uniq = [...new Set(notebooks.filter(n => !!n))];
  select.innerHTML = '<option value="">Todos</option>';
  uniq.forEach(nb => {
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
  const resp = await fetch('/notes', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, content, notebook, tags })
  }).catch(() => {});
  if (resp && resp.ok) {
    try { const created = await resp.json(); } catch (e) { /* ignore */ }
  }
  document.getElementById('noteForm').reset();
  await loadNotebooks();
  await loadNotes();
}

document.addEventListener('DOMContentLoaded', async () => {
  if (typeof window === 'undefined') return;
  document.getElementById('noteForm').addEventListener('submit', addNoteFromForm);
  await loadNotebooks();
  await loadNotes();
  document.getElementById('applyFilters').addEventListener('click', loadNotes);
});

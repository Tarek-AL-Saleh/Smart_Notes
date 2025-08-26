const API_URL = "https://smart-notes-avdl.onrender.com";

let notes = [];
let container = null
const emptyMessage = document.getElementById("emptyMessage");

const createNoteModal = document.getElementById("CreateNoteModal");
const closeCreateModal = document.getElementById("closeCreateNote");
const openCreateModalBtn = document.getElementById("openCreateNote");

const search = document.getElementById("searchQuery");
const searchBtn = document.getElementById("searchBtn");

let currentEditId = null;

const editNoteModal = document.getElementById("editNoteModal");
const editTitle = document.getElementById("editTitle");
const editContent = document.getElementById("editContent");
const editTags = document.getElementById("editTags");
const closeModal = document.getElementById("closeNoteEdit");
const saveEdit = document.getElementById("saveEdit");



// Fetch and display notes
async function fetchNotes() {
  const res = await fetch(`${API_URL}/notes`);
  container = document.getElementById("notesContainer");
  notes = await res.json();
  if (!notes.length) {
    emptyMessage.classList.remove("hidden"); // show message
    container.innerHTML = ""; // clear grid
    return;
  }
  else{
    emptyMessage.classList.add("hidden"); // hide message
    container.innerHTML = notes.map(renderNote).join("");
  }
}

// Create Notes from DB
function renderNote(note) {
    const dateLabel = note.updated_at
    ? `Updated at: ${new Date(note.updated_at).toLocaleString()}`
    : `Created at: ${new Date(note.created_at).toLocaleString()}`;

  return `
    <div class="bg-white rounded-xl shadow-lg p-6 hover:shadow-[0_20px_50px_rgba(0,0,0,0.4)] transform hover:scale-105 transition duration-300">
      <h3 class="text-2xl font-bold mb-2 text-purple-700">${note.title}</h3>
      <p class="text-gray-700 mb-4">${note.content}</p>
      <p class="text-sm text-gray-500 mb-4"><strong>Tags:</strong> ${(note.tags || []).join(", ") || "No tags"}</p>
      <p class="text-sm text-gray-600 mb-4"><strong>Summary:</strong> ${note.summary || "Not summarized yet"}</p>
      <p class="text-xs text-gray-400 mb-4">${dateLabel}</p>
      <div>
        <button onclick="summarizeNote('${note.id}')" class="bg-purple-500 m-1 text-white px-3 py-1 rounded hover:bg-purple-600 transition-colors">Summarize</button>
        <button onclick="editNote('${note.id}')" class="bg-blue-500 m-1 text-white px-3 py-1 rounded hover:bg-blue-600 transition-colors">Edit</button>
        <button onclick="deleteNote('${note.id}')" class="bg-red-500 m-1 text-white px-3 py-1 rounded hover:bg-red-600 transition-colors">Delete</button>
      </div>
    </div>
  `;
}

// Delete Note
async function deleteNote(id) {
  await fetch(`${API_URL}/notes/${id}`, { method: "DELETE" });
  fetchNotes();
}
// Summarize Note
async function summarizeNote(id) {
  await fetch(`${API_URL}/notes/${id}/summarize`, { method: "PUT" });
  fetchNotes();
}



///////////////////////// CREATE MODAL //////////////////////////////////////
// Open Create Note Modal
function createNote(noteId) {
  createNoteModal.classList.remove("hidden");
}
// Create Note
document.getElementById("createNoteBtn").addEventListener("click", async () => {
  const title = document.getElementById("title").value;
  const content = document.getElementById("content").value;
  const tags = document.getElementById("tags").value.split(",").map(t => t.trim()).filter(t => t);

  if (!title || !content) return alert("Title and Content are required!");

  const res = await fetch(`${API_URL}/notes/`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({title, content, tags})
  });
  if (res.ok) {
    fetchNotes();
    document.getElementById("title").value = "";
    document.getElementById("content").value = "";
    document.getElementById("tags").value = "";
    createNoteModal.classList.add("hidden");
  }
});
// Cancel Create Note
closeCreateModal.addEventListener("click", () => {
  createNoteModal.classList.add("hidden");
});
///////////////////////////////////////////////////////////////////////////// 



///////////////////////////// SEARCH FUNCTIONALITY ////////////////////////////////
// Search Notes
document.getElementById("searchBtn").addEventListener("click", async () => {
  const query = document.getElementById("searchQuery").value;
  if (!query) return fetchNotes();
  const res = await fetch(`${API_URL}/notes/filter/?query=${encodeURIComponent(query)}`);
  const notes = await res.json();
  const container = document.getElementById("notesContainer");
  container.innerHTML = notes.map(renderNote).join("");
});
// Trigger search on Enter key
search.addEventListener("keydown", function(event) {
  if (event.key === "Enter") {
    searchBtn.click();
  }
});
///////////////////////////////////////////////////////////////////////////////////



///////////////////////////// EDIT MODAL ////////////////////////////////////
// Open Edit modal
function editNote(noteId) {
  const note = notes.find(n => n.id === noteId);
  if (!note) return;

  currentEditId = noteId;
  editTitle.value = note.title;
  editContent.value = note.content;
  editTags.value = note.tags.join(", ");

  editNoteModal.classList.remove("hidden");
}

// Close Edit modal
closeNoteEdit.addEventListener("click", () => {
  editNoteModal.classList.add("hidden");
  currentEditId = null;
});

// Save Edit changes
saveEdit.addEventListener("click", () => {
  const title = editTitle.value.trim();
  const content = editContent.value.trim();
  const tags = editTags.value.split(",").map(t => t.trim()).filter(t => t);

  if (!title || !content) return alert("Title and Content required!");

  fetch(`${API_URL}/notes/${currentEditId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title, content, tags })
  })
  .then(res => res.json())
  .then(updatedNote => {
    const index = notes.findIndex(n => n.id === currentEditId);
    notes[index] = updatedNote;
    container.innerHTML = notes.map(renderNote).join("");

    editNoteModal.classList.add("hidden");
    currentEditId = null;
  })
  .catch(err => console.error(err));
});
///////////////////////////////////////////////////////////////////////////



// Initial fetch of notes
fetchNotes();
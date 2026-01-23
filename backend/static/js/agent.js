document.addEventListener("DOMContentLoaded", () => {

  const addModal = document.getElementById("addAgentModal");
  const deleteModal = document.getElementById("deleteAgentModal");

  const addBtn = document.getElementById("addAgentBtn");
  const deleteBtn = document.getElementById("deleteAgentBtn");

  const addForm = document.getElementById("addAgentForm");
  const deleteForm = document.getElementById("deleteAgentForm");

  /* OPEN MODALS */
  addBtn.onclick = () => addModal.style.display = "block";
  deleteBtn.onclick = () => deleteModal.style.display = "block";

  /* CLOSE MODALS */
  document.querySelectorAll(".close").forEach(btn => {
    btn.onclick = () => {
      addModal.style.display = "none";
      deleteModal.style.display = "none";
    };
  });

  window.onclick = e => {
    if (e.target === addModal) addModal.style.display = "none";
    if (e.target === deleteModal) deleteModal.style.display = "none";
  };

  /* ADD AGENT */
  addForm.onsubmit = e => {
    e.preventDefault();

    const data = Object.fromEntries(new FormData(addForm));
    console.log("ADD AGENT:", data);

    addForm.reset();
    addModal.style.display = "none";
  };

  /* DELETE AGENT */
  deleteForm.onsubmit = e => {
    e.preventDefault();

    const data = Object.fromEntries(new FormData(deleteForm));
    console.log("DELETE AGENT:", data);

    deleteForm.reset();
    deleteModal.style.display = "none";
  };

});

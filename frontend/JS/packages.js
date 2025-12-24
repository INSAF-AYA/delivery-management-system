document.addEventListener("DOMContentLoaded", () => {

  const addModal = document.getElementById("addPackageModal");
  const deleteModal = document.getElementById("deletePackageModal");

  const addBtn = document.getElementById("addPackageBtn");
  const deleteBtn = document.getElementById("deletePackageBtn");

  const addForm = document.getElementById("addPackageForm");
  const deleteForm = document.getElementById("deletePackageForm");

  /* OPEN */
  addBtn.onclick = () => addModal.style.display = "block";
  deleteBtn.onclick = () => deleteModal.style.display = "block";

  /* CLOSE */
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

  /* ADD PACKAGE */
  addForm.onsubmit = e => {
    e.preventDefault();

    const data = Object.fromEntries(new FormData(addForm));
    console.log("ADD PACKAGE:", data);

    addForm.reset();
    addModal.style.display = "none";
  };

  /* DELETE PACKAGE */
  deleteForm.onsubmit = e => {
    e.preventDefault();

    const data = Object.fromEntries(new FormData(deleteForm));
    console.log("DELETE PACKAGE:", data);

    deleteForm.reset();
    deleteModal.style.display = "none";
  };

});

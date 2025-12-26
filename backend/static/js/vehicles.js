document.addEventListener("DOMContentLoaded", () => {

  const addModal = document.getElementById("addVehicleModal");
  const deleteModal = document.getElementById("deleteVehicleModal");

  const addBtn = document.getElementById("addVehicleBtn");
  const deleteBtn = document.getElementById("deleteVehicleBtn");

  const addForm = document.getElementById("addVehicleForm");
  const deleteForm = document.getElementById("deleteVehicleForm");

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

  /* ADD VEHICLE */
  addForm.onsubmit = e => {
    e.preventDefault();

    const data = Object.fromEntries(new FormData(addForm));
    console.log("ADD VEHICLE:", data);

    addForm.reset();
    addModal.style.display = "none";
  };

  /* DELETE VEHICLE */
  deleteForm.onsubmit = e => {
    e.preventDefault();

    const data = Object.fromEntries(new FormData(deleteForm));
    console.log("DELETE VEHICLE:", data);

    deleteForm.reset();
    deleteModal.style.display = "none";
  };

});

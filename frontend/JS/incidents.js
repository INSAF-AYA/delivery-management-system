document.addEventListener("DOMContentLoaded", () => {

  const addModal = document.getElementById("addModal");
  const deleteModal = document.getElementById("deleteModal");

  document.getElementById("addBtn").onclick = () => {
    addModal.style.display = "block";
  };

  document.getElementById("deleteBtn").onclick = () => {
    deleteModal.style.display = "block";
  };

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

  document.getElementById("addIncidentForm").onsubmit = e => {
    e.preventDefault();
    console.log("ADD:", Object.fromEntries(new FormData(e.target)));
    e.target.reset();
    addModal.style.display = "none";
  };

  document.getElementById("deleteIncidentForm").onsubmit = e => {
    e.preventDefault();
    console.log("DELETE:", Object.fromEntries(new FormData(e.target)));
    e.target.reset();
    deleteModal.style.display = "none";
  };

});

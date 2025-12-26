document.addEventListener("DOMContentLoaded", () => {

  const addModal = document.getElementById("addDriverModal");
  const deleteModal = document.getElementById("deleteDriverModal");

  document.getElementById("addDriverBtn").onclick = () => {
    addModal.style.display = "block";
  };

  document.getElementById("deleteDriverBtn").onclick = () => {
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

  document.getElementById("addDriverForm").onsubmit = e => {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(e.target));
    console.log("ADD DRIVER:", data);
    e.target.reset();
    addModal.style.display = "none";
  };

  document.getElementById("deleteDriverForm").onsubmit = e => {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(e.target));
    console.log("DELETE DRIVER:", data);
    e.target.reset();
    deleteModal.style.display = "none";
  };

});

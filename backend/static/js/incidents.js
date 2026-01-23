document.addEventListener("DOMContentLoaded", () => {

  const addModal = document.getElementById("addInvoiceModal");
  const deleteModal = document.getElementById("deleteInvoiceModal");

  const addBtn = document.getElementById("addInvoiceBtn");
  const deleteBtn = document.getElementById("deleteInvoiceBtn");

  const addForm = document.getElementById("addInvoiceForm");
  const deleteForm = document.getElementById("deleteInvoiceForm");

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

  /* ADD INVOICE */
  addForm.onsubmit = e => {
    e.preventDefault();

    const data = new FormData(addForm); // includes PDF
    console.log("ADD INVOICE:");
    for (const pair of data.entries()) {
      console.log(pair[0], pair[1]);
    }

    addForm.reset();
    addModal.style.display = "none";
  };

  /* DELETE INVOICE */
  deleteForm.onsubmit = e => {
    e.preventDefault();

    const data = Object.fromEntries(new FormData(deleteForm));
    console.log("DELETE INVOICE:", data);

    deleteForm.reset();
    deleteModal.style.display = "none";
  };

});
document.addEventListener("DOMContentLoaded", () => {
    const addModal = document.getElementById("addAgentModal");
    const deleteModal = document.getElementById("deleteAgentModal");

    const addBtn = document.getElementById("addAgentBtn");
    const deleteBtn = document.getElementById("deleteAgentBtn");

    const addForm = document.getElementById("addAgentForm");
    const deleteForm = document.getElementById("deleteAgentForm");

    const tableBody = document.querySelector("table tbody");

    // CSRF helper
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + "=")) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Open modals
    addBtn.onclick = () => addModal.style.display = "block";
    deleteBtn.onclick = () => deleteModal.style.display = "block";

    // Close modals
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

    // Add Agent
    addForm.onsubmit = e => {
        e.preventDefault();
        const formData = new FormData(addForm);

        fetch("/agents/add/", {
            method: "POST",
            headers: { "X-CSRFToken": getCookie("csrftoken") },
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                alert("Agent added successfully!");
                loadAgents();
                addForm.reset();
                addModal.style.display = "none";
            } else {
                alert("Error: " + data.error);
            }
        });
    };

    // Delete Agent
    deleteForm.onsubmit = e => {
        e.preventDefault();
        const formData = new FormData(deleteForm);

        fetch("/agents/delete/", {
            method: "POST",
            headers: { "X-CSRFToken": getCookie("csrftoken") },
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                alert("Agent deleted successfully!");
                loadAgents();
                deleteForm.reset();
                deleteModal.style.display = "none";
            } else {
                alert("Error: " + data.error);
            }
        });
    };

    // Load agents in table
    function loadAgents() {
        fetch("/agents/")
        .then(res => res.json())
        .then(data => {
            tableBody.innerHTML = "";
            data.agents.forEach(agent => {
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td>${agent.agent_id}</td>
                    <td>${agent.nom} ${agent.prenom}</td>
                    <td>${agent.telephone}</td>
                    <td>${agent.date_embauche || ""}</td>
                    <td>${agent.role}</td>
                `;
                tableBody.appendChild(tr);
            });
        });
    }

    // Initial load
    loadAgents();
});

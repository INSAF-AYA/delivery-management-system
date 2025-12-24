const drvname =document.getElementById("driverName");/*the driver's info will change depending on the driver who log in */
const drvId =document.getElementById("driverId");

const elpending = document.getElementById("pending");/*the states of the shipments */
const elcomleted = document.getElementById("completed");
const eltotal = document.getElementById("total");






// affichage de la forme
document.getElementById('showFormBtn').addEventListener('click', function() {
    const form = document.getElementById('supportForm');
    form.classList.remove('d-none'); // bach yweli kayn display
    document.getElementById('formMessage').style.display = 'none'; 

    // Smooth scroll to the form
    form.scrollIntoView({ behavior: 'smooth', block: 'start' });
});

// boutton  de Cancel 
document.getElementById('cancelIssue').addEventListener('click', function() {
    const form = document.getElementById('supportForm');
    form.classList.add('d-none'); // bach la forme twli matbanch
    resetForm();
});

// boutton de submit
document.getElementById('submitIssue').addEventListener('click', function() {
    const issueType = document.getElementById('issueType');
    const description = document.getElementById('issueDesc');
    const message = document.getElementById('formMessage');

    let valid = true;

    
    if (!issueType.value) {
        issueType.classList.add('is-invalid');
        valid = false;
    } else {
        issueType.classList.remove('is-invalid');
    }


    if (!description.value.trim()) {
        description.classList.add('is-invalid');
        valid = false;
    } else {
        description.classList.remove('is-invalid');
    }

    if (!valid) return; 

    // la confirmation
    message.innerText = `Issue submitted! Type: ${issueType.value}, Description: ${description.value.trim()}`;
    message.style.display = 'block';

    


    issueType.value = '';
    description.value = '';
});


function resetForm() {
    const issueType = document.getElementById('issueType');
    const description = document.getElementById('issueDesc');
    const message = document.getElementById('formMessage');

    issueType.classList.remove('is-invalid');
    description.classList.remove('is-invalid');
    issueType.value = '';
    description.value = '';
    message.style.display = 'none';
}

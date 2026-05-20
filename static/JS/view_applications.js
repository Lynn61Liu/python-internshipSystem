document.addEventListener("DOMContentLoaded", function () {
  // add filter
  const form = document.getElementById("filterForm");
  const searchInput = document.getElementById("searchInput");
  const statusFilter = document.getElementById("statusFilter");
  const tableRows = document.querySelectorAll("tbody tr");

  form.addEventListener("submit", (e) => {
    e.preventDefault();

    const searchText = searchInput.value.toLowerCase().trim();
    const selectedStatus = statusFilter.value.toLowerCase();

    tableRows.forEach((row) => {
      const fullName = row.children[1].textContent.toLowerCase(); // Full Name column
      const internshipTitle = row.children[0].textContent.toLowerCase(); // Internship Title column
      const statusButton = row.children[8].querySelector("button");
      const status = statusButton.getAttribute("data-status");
      console.log("Row Full Name:", fullName);
      console.log(" searchText:", searchText);
      console.log("Row Internship Title:", internshipTitle);

      const matchText =
        fullName.includes(searchText) || internshipTitle.includes(searchText);
      const matchStatus = !selectedStatus || status === selectedStatus;
      console.log(" Match Text？？？？？？:", matchText);

      row.style.display = matchText && matchStatus ? "" : "none";
    });
  });
  const statusModal = document.getElementById("statusModal");
  statusModal.addEventListener("show.bs.modal", function (event) {
    const button = event.relatedTarget;
    const studentId = button.getAttribute("data-student-id");
    const internshipId = button.getAttribute("data-internship-id");
    const feedback = button.getAttribute("data-feedback");

    document.getElementById("modal-student-id").value = studentId;
    document.getElementById("modal-internship-id").value = internshipId;
    document.getElementById("feedback").value = feedback;
  });
  // view coverletter modal
  const coverLetterModal = document.getElementById("coverLetterModal");
  coverLetterModal.addEventListener("show.bs.modal", function (event) {
    const button = event.relatedTarget;
    const coverLetter = button.getAttribute("data-coverletter");
    const content = document.getElementById("coverLetterContent");
    content.textContent = coverLetter || "No cover letter available.";
  });
});

function submitStatus(status) {
  const studentId = document.getElementById("modal-student-id").value;
  const internshipId = document.getElementById("modal-internship-id").value;
  const newfeedback = document.getElementById("feedback").value;
  fetch("/update_application_status", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      student_id: studentId,
      internship_id: internshipId,
      status: status,
      feedback: newfeedback,
    }),
  }).then((res) => {
    console.log("Response from server=========:", res);

    if (res.ok) {
      location.reload();
    } else {
      alert("Error updating status");
    }
  });
}

function resetFilters() {
  document.getElementById("searchInput").value = "";
  document.getElementById("statusFilter").value = "";
  document.querySelectorAll("tbody tr").forEach((row) => {
    row.style.display = "";
  });
}

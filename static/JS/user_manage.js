document.addEventListener("DOMContentLoaded", function () {
  const modal = document.getElementById("statusModal");

  modal.addEventListener("show.bs.modal", function (event) {
    const button = event.relatedTarget;
    const userId = button.getAttribute("data-user-id");
    console.log(userId);

    document.getElementById("modal-student-id").value = userId;
  });

  const form = document.getElementById("filterForm");
  const firstNameInput = document.getElementById("searchFirstName");
  const lastNameInput = document.getElementById("searchLastName");
  const roleFilter = document.getElementById("roleFilter");
  const statusFilter = document.getElementById("statusFilter");
  const tableRows = document.querySelectorAll("tbody tr");

  form.addEventListener("submit", (e) => {
    e.preventDefault();

    const searchFirstName = firstNameInput.value.toLowerCase().trim();
    const searchLastName = lastNameInput.value.toLowerCase().trim();
    const selectedRole = roleFilter.value.toLowerCase();
    const selectedStatus = statusFilter.value.toLowerCase();

    console.log("First Name:", searchFirstName);
    console.log("Last Name:", searchLastName);
    console.log("Selected Role:", selectedRole);
    console.log("Selected Status:", selectedStatus);

    tableRows.forEach((row) => {
      const username = row.children[1].textContent.toLowerCase(); // Username
      const fullName = row.children[3].textContent.toLowerCase(); // Full Name
      const role = row.children[4].textContent.toLowerCase(); // Role
      const statusBtn = row.children[5].querySelector("button");
      const status = statusBtn
        ?.getAttribute("data-status")
        ?.trim()
        .toLowerCase();
      console.log("=======", status);

      let visible = true;

      if (searchFirstName && !username.includes(searchFirstName)) {
        visible = false;
      }
      if (searchLastName && !fullName.includes(searchLastName)) {
        visible = false;
      }
      if (selectedRole && role !== selectedRole) {
        visible = false;
      }
      if (selectedStatus && status !== selectedStatus) {
        visible = false;
      }

      row.style.display = visible ? "" : "none";
    });
  });
});

function submitStatus(newStatus) {
  console.log("Submitting status:", newStatus);

  const userId = document.getElementById("modal-student-id").value;

  fetch("/user/manage", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      user_id: userId,
      status: newStatus.toLowerCase(),
    }),
  })
    .then((response) => {
      if (!response.ok) {
        return response.json().then((data) => {
          throw new Error(data.error || "Unknown error");
        });
      }
      return response.json();
    })
    .then((data) => {
      console.log("Success:", data);
      location.reload();
    })
    .catch((error) => {
      alert("Error: " + error.message);
    });
}

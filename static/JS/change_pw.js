document.addEventListener("DOMContentLoaded", function () {
  log("Change Password JS loaded");
  const form = document.querySelector(".needs-validation");
  const newPw = document.getElementById("new_password");
  const confirmPw = document.getElementById("confirm_password");
  const submitBtn = document.getElementById("submit-btn");

  function validateMatch() {
    console.log("*********validateMatch do not match========");
    if (newPw.value && confirmPw.value && newPw.value === confirmPw.value) {
      confirmPw.classList.remove("is-invalid");
      confirmPw.classList.add("is-valid");
      submitBtn.disabled = false;
    } else {
      confirmPw.classList.remove("is-valid");
      confirmPw.classList.add("is-invalid");
      console.log("Passwords do not match========");

      submitBtn.disabled = true;
    }
  }

  newPw.addEventListener("input", validateMatch);
  confirmPw.addEventListener("input", validateMatch);
  confirmPw.addEventListener("blur", validateMatch);

  form.addEventListener("submit", function (event) {
    if (!form.checkValidity() || newPw.value !== confirmPw.value) {
      event.preventDefault();
      event.stopPropagation();
    }
    form.classList.add("was-validated");
  });
});

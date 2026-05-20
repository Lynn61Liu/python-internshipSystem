document.addEventListener("DOMContentLoaded", function () {
  const editBtn = document.getElementById("edit-btn");
  const cancelBtn = document.getElementById("cancel-btn");
  const editActions = document.getElementById("edit-actions");
  const editableFields = document.querySelectorAll(".editable-field");
  const deletePhotoBtn = document.getElementById("delete-photo-btn");
  const deletePhotoFlag = document.getElementById("delete-photo-flag");
  const photoInput = document.getElementById("photo");
  const adminPhoto = document.getElementById("adminPhoto");
  const profilePhotoPreview = document.getElementById("profile-photo-preview");
  const deleteLogoBtn = document.getElementById("delete-logo-btn");
  const logoPreview = document.getElementById("company-logo-preview");
  const deletelogoFlag = document.getElementById("delete-logo-flag");

  //admin profile image
  const deleteimageBtn = document.getElementById("delete-image-btn");
  const deleteimageFlag = document.getElementById("delete-image-flag");
  console.log("deleteimageFlag:", deleteimageFlag);

  const originalValues = {};
  editableFields.forEach((field) => {
    originalValues[field.id] = field.value;
  });

  editBtn.addEventListener("click", function () {
    ("Edit button clicked");
    editableFields.forEach((field) => (field.disabled = false));
    editBtn.style.display = "none";
    editActions.style.display = "flex";
    // Show delete photo button if a photo is uploaded
    if (deletePhotoBtn) deletePhotoBtn.style.display = "inline-block";
    if (deleteLogoBtn) deleteLogoBtn.style.display = "inline-block";
    // Show delete image button if an image is uploaded
    if (deleteimageBtn) deleteimageBtn.style.display = "inline-block";
  });

  cancelBtn.addEventListener("click", function () {
    editableFields.forEach((field) => {
      field.disabled = true;
      if (field.type !== "file") {
        field.value = originalValues[field.id];
      } else {
        field.value = "";
      }
    });
    editBtn.style.display = "inline-block";
    editActions.style.display = "none";
    // hide delete buttons
    if (deletePhotoBtn) deletePhotoBtn.style.display = "none";
    if (deleteLogoBtn) deleteLogoBtn.style.display = "none";
    if (deleteimageBtn) deleteimageBtn.style.display = "none";
  });
  //  delete photo button if a photo is uploaded
  if (deletePhotoBtn) {
    deletePhotoBtn.addEventListener("click", function () {
      profilePhotoPreview.src = "/static/images/default.jpg"; // Show default preview
      deletePhotoFlag.value = "true"; // Set deletion flag
      photoInput.value = "/static/images/default.jpg"; // Clear file input if any
    });
  }
  if (deleteLogoBtn) {
    deleteLogoBtn.addEventListener("click", function () {
      logoPreview.src = "/static/images/default.jpg"; // Show default preview
      deletelogoFlag.value = "true"; // Set deletion flag
    });
  }
  if (deleteimageBtn) {
    deleteimageBtn.addEventListener("click", function () {
      profilePhotoPreview.src = "/static/images/default.jpg"; // Show default preview
      deleteimageFlag.value = "true"; // Set deletion flag
      adminPhoto.value = "/static/images/default.jpg"; // Clear file input if any
    });
  }
});

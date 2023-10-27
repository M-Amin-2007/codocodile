function validateForm() {
    const form = document.getElementById('theForm')
    if (form.checkValidity()) {
        form.submit()
    } else {
        form.classList.add("was-validated");
    }
  }
  
  function validateLogin() {
    const form = document.getElementById('loginForm')
    if (form.checkValidity()) {
        form.submit()
    } else {
        form.classList.add("was-validated");
    }
  }
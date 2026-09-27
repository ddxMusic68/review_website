var dirBtn = document.getElementById("dir-toggle");
if (dirBtn) {
  dirBtn.addEventListener("click", function () {
    var dirInput = document.getElementById("sort-dir");
    dirInput.value = dirInput.value === "desc" ? "asc" : "desc";
    dirInput.form.submit();
  });
}

function applyView(view) {
  document.querySelectorAll(".video-list").forEach(function (section) {
    section.classList.toggle("hidden", section.dataset.view !== view);
  });
  document.querySelectorAll(".view-toggle .toggle-btn").forEach(function (b) {
    b.classList.toggle("active", b.dataset.view === view);
  });
}

document.querySelectorAll(".view-toggle .toggle-btn").forEach(function (button) {
  button.addEventListener("click", function () {
    var view = button.dataset.view;
    localStorage.setItem("view", view);
    applyView(view);
  });
});

applyView(localStorage.getItem("view") || "videos");

document.querySelectorAll(".star-widget").forEach(function (widget) {
  var input = widget.querySelector('input[type="hidden"]');
  var stars = widget.querySelectorAll(".star");
  var label = widget.querySelector(".star-value");

  function paint(active) {
    stars.forEach(function (star) {
      var value = parseInt(star.dataset.value, 10);
      var on = value <= active;
      star.classList.toggle("active", on);
      star.setAttribute("aria-pressed", on ? "true" : "false");
    });
  }

  function setValue(value) {
    input.value = value;
    label.textContent = value + "/" + stars.length;
    paint(value);
  }

  setValue(parseInt(input.value, 10) || 0);

  stars.forEach(function (star) {
    star.addEventListener("click", function () {
      setValue(parseInt(star.dataset.value, 10));
    });
    star.addEventListener("mouseenter", function () {
      paint(parseInt(star.dataset.value, 10));
    });
  });

  widget.addEventListener("mouseleave", function () {
    paint(parseInt(input.value, 10));
  });
});
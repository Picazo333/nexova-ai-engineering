(function () {
  var query = window.matchMedia("(prefers-reduced-motion: reduce)");
  function apply() {
    document.documentElement.setAttribute("data-motion", query.matches ? "reduced" : "full");
  }
  apply();
  if (query.addEventListener) {
    query.addEventListener("change", apply);
  } else if (query.addListener) {
    query.addListener(apply);
  }
})();

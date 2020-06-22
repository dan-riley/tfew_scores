var Signup = (function() {

  document.addEventListener('DOMContentLoaded', function(event) {
    // Initialize autocomplete
    var acdata = JSON.parse(document.getElementById("playersAuto").dataset.autocomplete);
    autocomplete(document.getElementsByName('name')[0], acdata);
  });
})();

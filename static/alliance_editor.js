var AllianceEditor = (function() {

  var alert_wrapper;

  document.addEventListener('DOMContentLoaded', function(event) {
    alert_wrapper = document.getElementById('alert_wrapper');
    // Initialize autocomplete
    if (document.getElementById("newNameAuto")) {
      var aldata = JSON.parse(document.getElementById("newNameAuto").dataset.autocomplete);
      autocomplete(document.getElementsByName('newName')[0], aldata);
    }

    // Setup the form submission and response
    initJSON(0, '/alliance_editor');
  });
})();

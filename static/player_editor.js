var PlayerEditor = (function() {

  var alert_wrapper;

  document.addEventListener('DOMContentLoaded', function(event) {
    alert_wrapper = document.getElementById('alert_wrapper');
    // Initialize autocomplete
    if (document.getElementById("newNameAuto")) {
      var pldata = JSON.parse(document.getElementById("newNameAuto").dataset.autocomplete);
      autocomplete(document.getElementsByName('newName')[0], pldata);
    }

    // Setup the form submission and response
    initJSON(1, '/player_editor');

    document.getElementById('alliance_id').addEventListener('change', function() {
      window.location.href = '/player_editor?alliance_id=' + this.value;
    });
  });
})();

var MovePlayer = (function() {

  var alert_wrapper;

  document.addEventListener('DOMContentLoaded', function(event) {
    alert_wrapper = document.getElementById('alert_wrapper');

    // Setup the form submission and response
    initJSON(0, '/move_player');
  });
})();

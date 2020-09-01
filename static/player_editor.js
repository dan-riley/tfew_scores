var PlayerEditor = (function() {

  var alert_wrapper;

  document.addEventListener('DOMContentLoaded', function(event) {
    alert_wrapper = document.getElementById('alert_wrapper');
    // Initialize autocomplete
    if (document.getElementById("newNameAuto")) {
      var pldata = JSON.parse(document.getElementById("newNameAuto").dataset.autocomplete);
      autocomplete(document.getElementsByName('newName')[0], pldata);
    }


    document.getElementById('submit').addEventListener('click', function() {
      var request = new XMLHttpRequest();
      request.addEventListener('load', function (e) {
          if (request.status == 200) {
            show_alert('Changes successfully saved', 'success');
          } else {
            show_alert('Error submitting changes', 'danger');
          }
      });

      data = $(document.forms[1]).serializeObject();
      request.responseType = 'json';
      request.open('POST', '/player_editor', true);
      request.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
      request.send(JSON.stringify(data));
    });

    document.getElementById('alliance_id').addEventListener('change', function() {
      window.location.href = '/player_editor?alliance_id=' + this.value;
    });
  });
})();

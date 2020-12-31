var PrimeEditor = (function() {

  var alert_wrapper;

  document.addEventListener('DOMContentLoaded', function(event) {
    alert_wrapper = document.getElementById('alert_wrapper');

    document.getElementById('submit').addEventListener('click', function() {
      var request = new XMLHttpRequest();
      request.addEventListener('load', function (e) {
          if (request.status == 200) {
            show_alert('Changes successfully saved', 'success');
          } else {
            show_alert('Error submitting changes', 'danger');
          }
      });

      data = $(document.forms[0]).serializeObject();
      request.responseType = 'json';
      request.open('POST', '/prime_editor', true);
      request.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
      request.send(JSON.stringify(data));
    });
  });
})();

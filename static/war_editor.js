var WarEditor = (function() {

  var alert_wrapper, players;

  document.addEventListener('DOMContentLoaded', function(event) {
    alert_wrapper = document.getElementById('alert_wrapper');
    players = document.querySelectorAll("input[name^=players][name*=score]");

    // Initialize autocomplete
    var oppdata = JSON.parse(document.getElementById("opponentsAuto").dataset.autocomplete);
    autocomplete(document.getElementsByName('opponent')[0], oppdata);

    // Setup auto-totaler for our score
    for (var i=0; i < players.length; i++) {
      players[i].addEventListener('blur', function() {
        var total = 0;
        for (var i=0; i < players.length; i++) {
          if (parseInt(players[i].value))
            total += parseInt(players[i].value)
        }

        document.getElementsByName('our_score')[0].value = total;
      });
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

      data = $(document.forms[0]).serializeObject();
      request.responseType = 'json';
      request.open('POST', '/war_editor', true);
      request.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
      request.send(JSON.stringify(data));
    });
  });
})();

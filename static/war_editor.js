var WarEditor = (function() {

  var alert_wrapper, players;
  var editor_table;
  var playerOrder;
  var scoreOrder;
  var lastSort = 0;

  document.addEventListener('DOMContentLoaded', function(event) {
    alert_wrapper = document.getElementById('alert_wrapper');

    // Initialize autocomplete
    var oppdata = JSON.parse(document.getElementById("opponentsAuto").dataset.autocomplete);
    autocomplete(document.getElementsByName('opponent_new')[0], oppdata);

    players = document.querySelectorAll("input[name^=players][name*=score], input[name^=missing_players][name*=score]");

    editor_table = document.getElementById('editor_table');
    addSortListeners();

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

    document.getElementById('alliance_id').addEventListener('change', function() {
      window.location.href = '/war_editor?alliance_id=' + this.value;
    });
  });

  function removeRow() {
    var row = document.getElementById('missingPlayersButtonRow');
    if (row)
      row.parentNode.removeChild(row);
  }

  function addSortListeners() {
    document.getElementById('player_sort').addEventListener('click', function() {
      removeRow();
      if (lastSort == 1)
        playerOrder = (playerOrder == 'asc') ? 'desc' : 'asc';
      else
        playerOrder = 'asc';
      lastSort = 1;
      sortTable(editor_table, lastSort, playerOrder)
    });

    document.getElementById('score_sort').addEventListener('click', function() {
      removeRow();
      if (lastSort == 2)
        scoreOrder = (scoreOrder == 'asc') ? 'desc' : 'asc';
      else
        scoreOrder = 'desc';
      lastSort = 2;
      sortTable(editor_table, lastSort, scoreOrder)
    });
  }
})();

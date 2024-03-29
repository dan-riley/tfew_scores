var WarEditor = (function() {

  var alert_wrapper, players;
  var editor_table;
  var playerOrder;
  var scoreOrder;
  var aiOrder;
  var missingRow;
  var lastSort = 0;
  var dblValue = 300;

  document.addEventListener('DOMContentLoaded', function(event) {
    alert_wrapper = document.getElementById('alert_wrapper');

    // Initialize autocomplete
    var oppdata = JSON.parse(document.getElementById("opponentsAuto").dataset.autocomplete);
    autocomplete(document.getElementsByName('opponent_new')[0], oppdata);

    players = document.querySelectorAll("input[name^=players][name*=score], input[name^=missing_players][name*=score]");

    editor_table = document.getElementById('editor_table');
    addSortListeners();
    addScoreListeners(players);

    // Setup auto-totaler for our score
    for (var i=0; i < players.length; i++) {
      players[i].addEventListener('blur', function() {
        if (this.value % 5 != 0)
          this.style.backgroundColor = 'red';
        else if (this.style.backgroundColor == 'red')
          this.style.backgroundColor = '';

        dblValue = this.value
        totalScores();
      });

      players[i].addEventListener('dblclick', function() {
        if ((this.value == '') || (this.value == '300'))
          this.value = dblValue;
      });
    }

    // Setup the form submission and response
    initJSON(0, '/war_editor');

    document.getElementById('alliance_id').addEventListener('change', function() {
      window.location.href = '/war_editor?alliance_id=' + this.value;
    });

    document.getElementById('toggle_upload_btn').addEventListener('click', function() {
      document.getElementById('upload_group').classList.remove('hide');
      document.getElementById('toggle_upload').classList.add('hide');
      var ai_cols = document.getElementsByClassName('ai-col');
      for (let col of ai_cols) {
        col.classList.remove('hide');
      }
    });
  });

  function totalScores() {
    var total = 0;
    for (var i=0; i < players.length; i++) {
      if (parseInt(players[i].value))
        total += parseInt(players[i].value)
    }

    document.getElementsByName('our_score')[0].value = total;
  }

  function removeRow() {
    // Remove the missing players button for sorting, but save to re-add
    missingRow = document.getElementById('missingPlayersButtonRow');
    if (missingRow)
      missingRow.parentNode.removeChild(missingRow);
  }

  function reAddRow() {
    // Re-add the missing players button
    if (missingRow)
      editor_table.appendChild(missingRow);
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
      reAddRow();
    });

    document.getElementById('score_sort').addEventListener('click', function() {
      removeRow();
      if (lastSort == 2)
        scoreOrder = (scoreOrder == 'asc') ? 'desc' : 'asc';
      else
        scoreOrder = 'desc';
      lastSort = 2;
      sortTable(editor_table, lastSort, scoreOrder)
      reAddRow();
    });

    document.getElementById('ai_sort').addEventListener('click', function() {
      // Put the blanks at the bottom
      ai = document.querySelectorAll("div[id*=airank]");
      for (a of ai) {
        if (a.innerHTML.trim() == '')
          a.innerHTML = '99';
      }

      removeRow();
      if (lastSort == 3)
        aiOrder = (aiOrder == 'asc') ? 'desc' : 'asc';
      else
        aiOrder = 'asc';
      lastSort = 3;
      sortTable(editor_table, lastSort, aiOrder)
      reAddRow();

      // Get the blanks back
      for (a of ai) {
        if (a.innerHTML == '99')
          a.innerHTML = '';
      }
    });
  }

  function addScoreListeners(players) {
    document.getElementById('setAll300').addEventListener('click', function() {
      for (var i=0; i < players.length; i++) {
        players[i].value = 300;
      }
      totalScores();
    });

    document.getElementById('resetAll').addEventListener('click', function() {
      for (var i=0; i < players.length; i++) {
        players[i].value = '';
      }
      totalScores();
    });
  }
})();

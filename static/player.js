var trackedChart = true;
var untrackedChart = false;
var primeChart = false;
var cyberChart = false;
var allChart = true;
var addCol = 0;

var Player = (function() {

  var player_table;
  var dateOrder;
  var allianceOrder;
  var opponentOrder;
  var leagueOrder;
  var pointsOrder;
  var baseOrder;
  var scoreOrder;
  var lastSort = 0;

  var ScoreOptions = {
    title: 'Player Scores',
    interpolateNulls: true,
    trendlines: {
      0: {
        title: 'All Trend',
        type: 'polynomial',
        degree: 3,
        visibleInLegend: false,
      },
      1: {
        title: 'Tracked Trend',
        type: 'polynomial',
        degree: 3,
        visibleInLegend: false,
      },
      2: {
        title: 'Untracked Trend',
        type: 'polynomial',
        degree: 3,
        visibleInLegend: false,
      },
      3: {
        title: 'Prime Trend',
        type: 'polynomial',
        degree: 3,
        visibleInLegend: false,
      },
      4: {
        title: 'Cybertron Trend',
        type: 'polynomial',
        degree: 3,
        visibleInLegend: false,
      }
    }
  };

  document.addEventListener('DOMContentLoaded', function(event) {
    // Initialize autocomplete
    if (document.getElementById("playersAuto")) {
      var pldata = JSON.parse(document.getElementById("playersAuto").dataset.autocomplete);
      autocomplete(document.getElementsByName('player')[0], pldata);
    }

    // If we're showing the alliance column, adjust the ones after
    if (document.getElementById("alliance_sort")) addCol = 1;

    player_table = document.getElementById('player_table');
    addSortListeners();
    addZoomListeners(player_table);
    addTableToggles();
    addChartToggles();

    buildChart('chart_Score', 'getScoreData', ScoreOptions, 'line');
  });

  function addSortListeners() {
    document.getElementById('date_sort').addEventListener('click', function() {
      if (lastSort == 1)
        dateOrder = (dateOrder == 'asc') ? 'desc' : 'asc';
      else
        dateOrder = 'asc';
      lastSort = 1;
      sortTable(player_table, lastSort, dateOrder)
      buildChart('chart_Score', 'getScoreData', ScoreOptions, 'line');
    });

    if (document.getElementById("alliance_sort")) {
      document.getElementById('alliance_sort').addEventListener('click', function() {
        if (lastSort == 2)
          allianceOrder = (allianceOrder == 'asc') ? 'desc' : 'asc';
        else
          allianceOrder = 'asc';
        lastSort = 2;
        sortTable(player_table, lastSort, allianceOrder)
      });
    }

    document.getElementById('opponent_sort').addEventListener('click', function() {
      if (lastSort == 2 + addCol)
        opponentOrder = (opponentOrder == 'asc') ? 'desc' : 'asc';
      else
        opponentOrder = 'asc';
      lastSort = 2 + addCol;
      sortTable(player_table, lastSort, opponentOrder)
    });

    document.getElementById('league_sort').addEventListener('click', function() {
      if (lastSort == 3 + addCol)
        leagueOrder = (leagueOrder == 'asc') ? 'desc' : 'asc';
      else
        leagueOrder = 'desc';
      lastSort = 3 + addCol;
      sortTable(player_table, lastSort, leagueOrder)
    });

    document.getElementById('points_sort').addEventListener('click', function() {
      if (lastSort == 4 + addCol)
        pointsOrder = (pointsOrder == 'asc') ? 'desc' : 'asc';
      else
        pointsOrder = 'desc';
      lastSort = 4 + addCol;
      sortTable(player_table, lastSort, pointsOrder)
    });

    document.getElementById('base_sort').addEventListener('click', function() {
      if (lastSort == 5 + addCol)
        baseOrder = (baseOrder == 'asc') ? 'desc' : 'asc';
      else
        baseOrder = 'desc';
      lastSort = 5 + addCol;
      sortTable(player_table, lastSort, baseOrder)
    });

    document.getElementById('score_sort').addEventListener('click', function() {
      if (lastSort == 6 + addCol)
        scoreOrder = (scoreOrder == 'asc') ? 'desc' : 'asc';
      else
        scoreOrder = 'desc';
      lastSort = 6 + addCol;
      sortTable(player_table, lastSort, scoreOrder)
    });
  }

  function togglePlayerRows(check, table, skip, col, value) {
    // Checkboxes
    var trackedTable = document.getElementsByName('tracked_table')[0];
    var untrackedTable = document.getElementsByName('untracked_table')[0];
    var primeTable = document.getElementsByName('prime_table')[0];
    var cyberTable = document.getElementsByName('cyber_table')[0];
    var allTable = document.getElementsByName('all_table')[0];

    var rows = Array.from(player_table.querySelectorAll('tr'));
    rows = rows.slice(1);
    rank = 1;
    rows.forEach(function(row) {
      // Default to off, then turn on each type individually
      row.style.display = 'none';
      if (trackedTable.checked) {
        // Show both tracked and optional in the table
        if (row.children[0].children[1].value != 0) {
          row.style.display = 'table-row';
        }
      }
      if (untrackedTable.checked) {
        if (row.children[0].children[1].value == 0) {
          row.style.display = 'table-row';
        }
      }
      if (primeTable.checked) {
        if (row.children[2].innerText.trim() == 'Prime') {
          row.style.display = 'table-row';
        }
      }
      if (cyberTable.checked) {
        if (row.children[2].innerText.trim() == 'Cybertron') {
          row.style.display = 'table-row';
        }
      }
      player_table.appendChild(row);
    });
  }

  function addTableToggles() {
    document.getElementById('alliance_history_toggle').addEventListener('click', function() {
      var div = document.getElementById('alliance_history');
      if (div.style.display == 'none') {
        div.style.display = 'block';
        this.innerHTML = 'Alliance History -'
      } else {
        div.style.display = 'none';
        this.innerHTML = 'Alliance History +<br /><br />'
      }
    });

    // Set the checkmarks depending on other checkmarks, then rebuild the table
    document.getElementsByName('tracked_table')[0].addEventListener('change', function() {
      if (!this.checked) {
        document.getElementsByName('all_table')[0].checked = this.checked;
      }
      togglePlayerRows();
    });
    document.getElementsByName('untracked_table')[0].addEventListener('change', function() {
      if (!this.checked) {
        document.getElementsByName('all_table')[0].checked = this.checked;
      }
      togglePlayerRows();
    });
    document.getElementsByName('prime_table')[0].addEventListener('change', function() {
      if (!this.checked) {
        document.getElementsByName('all_table')[0].checked = this.checked;
      }
      togglePlayerRows();
    });
    document.getElementsByName('cyber_table')[0].addEventListener('change', function() {
      if (!this.checked) {
        document.getElementsByName('all_table')[0].checked = this.checked;
      }
      togglePlayerRows();
    });
    document.getElementsByName('all_table')[0].addEventListener('change', function() {
      // If enabled then make all enabled
      if (this.checked) {
        document.getElementsByName('tracked_table')[0].checked = this.checked;
        document.getElementsByName('untracked_table')[0].checked = this.checked;
        document.getElementsByName('prime_table')[0].checked = this.checked;
        document.getElementsByName('cyber_table')[0].checked = this.checked;
      }
      togglePlayerRows();
    });
  }

  function addChartToggles() {
    // Rebuild the chart and turn columns on and off based on checkmark
    document.getElementsByName('tracked_chart')[0].addEventListener('change', function() {
      trackedChart = this.checked;
      buildChart('chart_Score', 'getScoreData', ScoreOptions, 'line');
    });
    document.getElementsByName('untracked_chart')[0].addEventListener('change', function() {
      untrackedChart = this.checked;
      buildChart('chart_Score', 'getScoreData', ScoreOptions, 'line');
    });
    document.getElementsByName('prime_chart')[0].addEventListener('change', function() {
      primeChart = this.checked;
      buildChart('chart_Score', 'getScoreData', ScoreOptions, 'line');
    });
    document.getElementsByName('cyber_chart')[0].addEventListener('change', function() {
      cyberChart = this.checked;
      buildChart('chart_Score', 'getScoreData', ScoreOptions, 'line');
    });
    document.getElementsByName('all_chart')[0].addEventListener('change', function() {
      allChart = this.checked;
      buildChart('chart_Score', 'getScoreData', ScoreOptions, 'line');
    });
  }
})();

function getScoreData() {
  // Load data from the table.  Change this to load once so sorting doesn't affect it.
  var data = new google.visualization.DataTable();
  var results = document.getElementById('player_table');
  Array.prototype.forEach.call(results.rows, function (row) {
    var tableColumns = [];

    if (row.rowIndex == 0) {
      data.addColumn('date', 'Date');
      data.addColumn('number', 'All');
      data.addColumn('number', 'Tracked');
      data.addColumn('number', 'Untracked');
      data.addColumn('number', 'Prime');
      data.addColumn('number', 'Cybertron');
    } else {
      // Need null values for dates to exclude from each category
      var score = parseInt(row.cells[5 + addCol].innerText);
      var tracked = null;
      if (row.cells[0].children[1].value == '1')
        // Only show tracked on the chart, not optional
        tracked = score;
      var untracked = null;
      if (row.cells[0].children[1].value == '0')
        untracked = score;
      var prime = null;
      if (row.cells[2 + addCol].innerText == 'Prime')
        prime = score;
      var cyber = null;
      if (row.cells[2 + addCol].innerText == 'Cybertron')
        cyber = score;

      datearr = row.cells[0].innerText.split('-')
      date = new Date(datearr[0], datearr[1]-1, datearr[2]);
      data.addRow([date, score, tracked, untracked, prime, cyber]);
    }
  });

  // Set the columns to display based on what's checked
  cols = Array();
  cols.push(0);
  if (allChart) cols.push(1);
  if (trackedChart) cols.push(2);
  if (untrackedChart) cols.push(3);
  if (primeChart) cols.push(4);
  if (cyberChart) cols.push(5);

  return [data, cols];
}

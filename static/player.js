var Player = (function() {

  var player_table;
  var dateOrder;
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
        title: 'Total Trend',
        type: 'polynomial',
        degree: 3,
        visibleInLegend: false,
      },
      1: {
        title: 'Prime Trend',
        type: 'polynomial',
        degree: 3,
        visibleInLegend: false,
      }
    }

  };

  document.addEventListener('DOMContentLoaded', function(event) {
    // Initialize autocomplete
    var pldata = JSON.parse(document.getElementById("playersAuto").dataset.autocomplete);
    autocomplete(document.getElementsByName('player')[0], pldata);

    var oppdata = JSON.parse(document.getElementById("opponentsAuto").dataset.autocomplete);
    autocomplete(document.getElementsByName('opponent')[0], oppdata);

    player_table = document.getElementById('player_table');
    addSortListeners();

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

    document.getElementById('opponent_sort').addEventListener('click', function() {
      if (lastSort == 2)
        opponentOrder = (opponentOrder == 'asc') ? 'desc' : 'asc';
      else
        opponentOrder = 'asc';
      lastSort = 2;
      sortTable(player_table, lastSort, opponentOrder)
    });

    document.getElementById('league_sort').addEventListener('click', function() {
      if (lastSort == 3)
        leagueOrder = (leagueOrder == 'asc') ? 'desc' : 'asc';
      else
        leagueOrder = 'desc';
      lastSort = 3;
      sortTable(player_table, lastSort, leagueOrder)
      buildChart('chart_Score', 'getScoreData', ScoreOptions, 'line');
    });

    document.getElementById('points_sort').addEventListener('click', function() {
      if (lastSort == 4)
        pointsOrder = (pointsOrder == 'asc') ? 'desc' : 'asc';
      else
        pointsOrder = 'desc';
      lastSort = 4;
      sortTable(player_table, lastSort, pointsOrder)
    });

    document.getElementById('base_sort').addEventListener('click', function() {
      if (lastSort == 5)
        baseOrder = (baseOrder == 'asc') ? 'desc' : 'asc';
      else
        baseOrder = 'desc';
      lastSort = 5;
      sortTable(player_table, lastSort, baseOrder)
    });

    document.getElementById('score_sort').addEventListener('click', function() {
      if (lastSort == 6)
        scoreOrder = (scoreOrder == 'asc') ? 'desc' : 'asc';
      else
        scoreOrder = 'desc';
      lastSort = 6;
      sortTable(player_table, lastSort, scoreOrder)
    });
  }
})();

function getScoreData() {
  var data = new google.visualization.DataTable();
  var results = document.getElementById('player_table');
  Array.prototype.forEach.call(results.rows, function (row) {
    var tableColumns = [];

    if (row.rowIndex == 0) {
      data.addColumn('date', 'Date');
      data.addColumn('number', 'Total');
      data.addColumn('number', 'Prime');
    } else {
      var prime = null;
      if (row.cells[2].innerText == 'Prime')
        prime = parseInt(row.cells[5].innerText);

      data.addRow([new Date(row.cells[0].innerText + ' 00:00'), parseInt(row.cells[5].innerText), prime]);
    }
  });

  return data;
}

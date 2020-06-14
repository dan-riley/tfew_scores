var Main = (function() {

  var player_table;
  var dateOrder;
  var opponentOrder;
  var leagueOrder;
  var pointsOrder;
  var baseOrder;
  var scoreOrder;
  var lastSort = 0;

  document.addEventListener('DOMContentLoaded', function(event) {
    // Initialize autocomplete
    var acdata = JSON.parse(document.getElementById("opponentsAuto").dataset.autocomplete);
    autocomplete(document.getElementsByName('opponent')[0], acdata);

    player_table = document.getElementById('player_table');
    addSortListeners();
  });

  function addSortListeners() {
    document.getElementById('date_sort').addEventListener('click', function() {
      if (lastSort == 1)
        dateOrder = (dateOrder == 'asc') ? 'desc' : 'asc';
      else
        dateOrder = 'asc';
      lastSort = 1;
      sortTable(player_table, lastSort, dateOrder)
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
        baseSort = (baseSort == 'asc') ? 'desc' : 'asc';
      else
        baseSort = 'desc';
      lastSort = 5;
      sortTable(player_table, lastSort, baseSort)
    });

    document.getElementById('score_sort').addEventListener('click', function() {
      if (lastSort == 6)
        scoreSort = (baseSort == 'asc') ? 'desc' : 'asc';
      else
        scoreSort = 'desc';
      lastSort = 6;
      sortTable(player_table, lastSort, scoreSort)
    });
  }
})();

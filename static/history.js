var History = (function() {

  var history_table;
  var dateOrder;
  var opponentOrder;
  var leagueOrder;
  var ourPointsOrder;
  var oppPointsOrder;
  var lastSort = 0;

  document.addEventListener('DOMContentLoaded', function(event) {
    // Initialize autocomplete
    var acdata = JSON.parse(document.getElementById("opponentsAuto").dataset.autocomplete);
    autocomplete(document.getElementsByName('opponent')[0], acdata);

    history_table = document.getElementById('history_table');
    addSortListeners();
    addZoomListeners(history_table);
    toggleRows('tracked_only', history_table, 1, 0, '0');
  });

  function addSortListeners() {
    document.getElementById('date_sort').addEventListener('click', function() {
      if (lastSort == 1)
        dateOrder = (dateOrder == 'asc') ? 'desc' : 'asc';
      else
        dateOrder = 'asc';
      lastSort = 1;
      sortTable(history_table, lastSort, dateOrder)
    });

    document.getElementById('opponent_sort').addEventListener('click', function() {
      if (lastSort == 2)
        opponentOrder = (opponentOrder == 'asc') ? 'desc' : 'asc';
      else
        opponentOrder = 'asc';
      lastSort = 2;
      sortTable(history_table, lastSort, opponentOrder)
    });

    document.getElementById('league_sort').addEventListener('click', function() {
      if (lastSort == 3)
        leagueOrder = (leagueOrder == 'asc') ? 'desc' : 'asc';
      else
        leagueOrder = 'desc';
      lastSort = 3;
      sortTable(history_table, lastSort, leagueOrder)
    });

    document.getElementById('our_points_sort').addEventListener('click', function() {
      if (lastSort == 4)
        ourPointsOrder = (ourPointsOrder == 'asc') ? 'desc' : 'asc';
      else
        ourPointsOrder = 'desc';
      lastSort = 4;
      sortTable(history_table, lastSort, ourPointsOrder)
    });

    document.getElementById('opp_points_sort').addEventListener('click', function() {
      if (lastSort == 5)
        oppPointsOrder = (oppPointsOrder == 'asc') ? 'desc' : 'asc';
      else
        oppPointsOrder = 'desc';
      lastSort = 5;
      sortTable(history_table, lastSort, oppPointsOrder)
    });
  }
})();

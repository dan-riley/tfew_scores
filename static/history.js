var History = (function() {

  var history_table;
  var dateOrder;
  var allianceOrder;
  var opponentOrder;
  var leagueOrder;
  var ourPointsOrder;
  var oppPointsOrder;
  var lastSort = 0;
  var addCol = 0;

  document.addEventListener('DOMContentLoaded', function(event) {
    // If we're showing the alliance column, adjust the ones after
    if (document.getElementById("alliance_sort")) addCol = 1;

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

    if (document.getElementById("alliance_sort")) {
      document.getElementById('alliance_sort').addEventListener('click', function() {
        if (lastSort == 2)
          allianceOrder = (allianceOrder == 'asc') ? 'desc' : 'asc';
        else
          allianceOrder = 'asc';
        lastSort = 2;
        sortTable(history_table, lastSort, allianceOrder)
      });
    }

    document.getElementById('opponent_sort').addEventListener('click', function() {
      if (lastSort == 2 + addCol)
        opponentOrder = (opponentOrder == 'asc') ? 'desc' : 'asc';
      else
        opponentOrder = 'asc';
      lastSort = 2 + addCol;
      sortTable(history_table, lastSort, opponentOrder)
    });

    document.getElementById('league_sort').addEventListener('click', function() {
      if (lastSort == 3 + addCol)
        leagueOrder = (leagueOrder == 'asc') ? 'desc' : 'asc';
      else
        leagueOrder = 'desc';
      lastSort = 3 + addCol;
      sortTable(history_table, lastSort, leagueOrder)
    });

    document.getElementById('our_points_sort').addEventListener('click', function() {
      if (lastSort == 4 + addCol)
        ourPointsOrder = (ourPointsOrder == 'asc') ? 'desc' : 'asc';
      else
        ourPointsOrder = 'desc';
      lastSort = 4 + addCol;
      sortTable(history_table, lastSort, ourPointsOrder)
    });

    document.getElementById('opp_points_sort').addEventListener('click', function() {
      if (lastSort == 5 + addCol)
        oppPointsOrder = (oppPointsOrder == 'asc') ? 'desc' : 'asc';
      else
        oppPointsOrder = 'desc';
      lastSort = 5 + addCol;
      sortTable(history_table, lastSort, oppPointsOrder)
    });
  }
})();

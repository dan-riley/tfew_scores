var Main = (function() {

  var players;
  var summary_table;
  var playerOrder;
  var trackedOrder;
  var untrackedOrder;
  var primeOrder;
  var allOrder;
  var lastSort = 0;
  var skip = 12;

  document.addEventListener('DOMContentLoaded', function(event) {
    // Initialize autocomplete
    var acdata = JSON.parse(document.getElementById("opponentsAuto").dataset.autocomplete);
    autocomplete(document.getElementsByName('opponent')[0], acdata);

    summary_table = document.getElementById('summary_table');
    addSortListeners();
    addZoomListeners(summary_table);
    toggleRows('active_only', summary_table, 12, 1, 'False');
    toggleColumns('tracked_only', summary_table, 3, 'No');
  });

  function addSortListeners() {
    document.getElementById('player_sort').addEventListener('click', function() {
      if (lastSort == 2)
        playerOrder = (playerOrder == 'asc') ? 'desc' : 'asc';
      else
        playerOrder = 'asc';
      lastSort = 2;
      sortTable(summary_table, lastSort, playerOrder, skip)
    });

    document.getElementById('tracked_sort').addEventListener('click', function() {
      if (lastSort == 3)
        trackedOrder = (trackedOrder == 'asc') ? 'desc' : 'asc';
      else
        trackedOrder = 'desc';
      lastSort = 3;
      sortTable(summary_table, lastSort, trackedOrder, skip)
    });

    document.getElementById('untracked_sort').addEventListener('click', function() {
      if (lastSort == 4)
        untrackedOrder = (untrackedOrder == 'asc') ? 'desc' : 'asc';
      else
        untrackedOrder = 'desc';
      lastSort = 4;
      sortTable(summary_table, lastSort, untrackedOrder, skip)
    });

    document.getElementById('prime_sort').addEventListener('click', function() {
      if (lastSort == 5)
        primeOrder = (primeOrder == 'asc') ? 'desc' : 'asc';
      else
        primeOrder = 'desc';
      lastSort = 5;
      sortTable(summary_table, lastSort, primeOrder, skip)
    });

    document.getElementById('all_sort').addEventListener('click', function() {
      if (lastSort == 6)
        allOrder = (allOrder == 'asc') ? 'desc' : 'asc';
      else
        allOrder = 'desc';
      lastSort = 6;
      sortTable(summary_table, lastSort, allOrder, skip)
    });
  }
})();

var Main = (function() {

  var players;
  var summary_table;
  var playerOrder;
  var trackedOrder;
  var untrackedOrder;
  var primeOrder;
  var totalOrder;
  var lastSort = 0;
  var skip = 12;

  document.addEventListener('DOMContentLoaded', function(event) {
    // Initialize autocomplete
    var acdata = JSON.parse(document.getElementById("opponentsAuto").dataset.autocomplete);
    autocomplete(document.getElementsByName('opponent')[0], acdata);

    summary_table = document.getElementById('summary_table');
    addSortListeners();
  });

  function addSortListeners() {
    document.getElementById('player_sort').addEventListener('click', function() {
      if (lastSort == 1)
        playerOrder = (playerOrder == 'asc') ? 'desc' : 'asc';
      else
        playerOrder = 'asc';
      lastSort = 1;
      sortTable(summary_table, lastSort, playerOrder, skip)
    });

    document.getElementById('tracked_sort').addEventListener('click', function() {
      if (lastSort == 2)
        trackedOrder = (trackedOrder == 'asc') ? 'desc' : 'asc';
      else
        trackedOrder = 'desc';
      lastSort = 2;
      sortTable(summary_table, lastSort, trackedOrder, skip)
    });

    document.getElementById('untracked_sort').addEventListener('click', function() {
      if (lastSort == 3)
        untrackedOrder = (untrackedOrder == 'asc') ? 'desc' : 'asc';
      else
        untrackedOrder = 'desc';
      lastSort = 3;
      sortTable(summary_table, lastSort, untrackedOrder, skip)
    });

    document.getElementById('prime_sort').addEventListener('click', function() {
      if (lastSort == 4)
        primeOrder = (primeOrder == 'asc') ? 'desc' : 'asc';
      else
        primeOrder = 'desc';
      lastSort = 4;
      sortTable(summary_table, lastSort, primeOrder, skip)
    });

    document.getElementById('total_sort').addEventListener('click', function() {
      if (lastSort == 5)
        totalOrder = (totalOrder == 'asc') ? 'desc' : 'asc';
      else
        totalOrder = 'desc';
      lastSort = 5;
      sortTable(summary_table, lastSort, totalOrder, skip)
    });
  }
})();

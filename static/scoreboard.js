var Main = (function() {

  var players;
  var summary_table;
  var playerOrder = 'asc';
  var trackedOrder;
  var untrackedOrder;
  var primeOrder;
  var allOrder;
  var lastSort = 2;
  var skip = 12;

  document.addEventListener('DOMContentLoaded', function(event) {
    // Initialize autocomplete
    var acdata = JSON.parse(document.getElementById("opponentsAuto").dataset.autocomplete);
    autocomplete(document.getElementsByName('opponent')[0], acdata);

    summary_table = document.getElementById('summary_table');
    // Initialize listeners
    addSortListeners();
    addZoomListeners(summary_table);
    // Setup the listeners to toggle rows and columns off
    toggleRows('active_only', summary_table, skip, 1, 'False', 'getAverages', [summary_table, skip]);
    toggleColumns('tracked_only', summary_table, 3, 'No');
    // Set Active Only by default
    checkBox(document.getElementsByName('active_only')[0]);

    // Get the players averages before sorting
    getAverages(summary_table, skip);

    // If regular player is logged in, and tracked is default sort, execute it
    tracked_check = document.getElementById('tracked_sort');
    if (tracked_check.classList.contains('sorted-down')) {
      triggerEvent(tracked_check, 'click');
    }
  });

  function addSortListeners() {
    document.getElementById('player_sort').addEventListener('click', function() {
      if (this.classList.contains('nosort'))
        return;
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

function getAverages(table, skip) {
  tracked = 0;
  untracked = 0;
  prime = 0;
  all = 0;
  count = 0;
  var rows = Array.from(table.querySelectorAll('tr'));
  rows = rows.slice(skip);
  rows.forEach(function(row) {
    if ((row.style.display != 'none') && (row.children[1].children[0].innerText.trim() != 'Average')) {
      tracked += parseInt(row.children[2].innerText);
      untracked += parseInt(row.children[3].innerText);
      prime += parseInt(row.children[4].innerText);
      all += parseInt(row.children[5].innerText);
      count += 1;
    }
  });

  document.getElementById('avg_tracked').innerText = Math.round(tracked / count);
  document.getElementById('avg_untracked').innerText = Math.round(untracked / count);
  document.getElementById('avg_prime').innerText = Math.round(prime / count);
  document.getElementById('avg_all').innerText = Math.round(all / count);
}

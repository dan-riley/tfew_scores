var Main = (function() {

  var players;
  var summary_table;
  var playerOrder = 'asc';
  var trackedOrder;
  var rawOrder;
  var untrackedOrder;
  var primeOrder;
  var allOrder;
  var dropsOrder;
  var strikeOrder;
  var lastSort = 2;
  var skip = 12;

  document.addEventListener('DOMContentLoaded', function(event) {
    summary_table = document.getElementById('summary_table');
    // Initialize listeners
    addSortListeners();
    addZoomListeners(summary_table);
    // Setup the listeners to toggle rows and columns off
    toggleRows('active_only', summary_table, skip, 1, 'False', 'getAverages', [summary_table, skip]);
    toggleColumns('tracked_only', summary_table, 3, 'No');
    // Listen for toggling the optional averages
    toggleAverages(summary_table);
    triggerEvent(document.getElementById('col-toggle'), 'click');

    // Set Active Only by default
    checkBox(document.getElementsByName('active_only')[0]);

    // Get the players averages before sorting
    getAverages(summary_table, skip);

    // Sort by tracked average, then all average, then player (starts as player)
    triggerEvent(document.getElementById('all_sort'), 'click');
    triggerEvent(document.getElementById('tracked_sort'), 'click');
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

    document.getElementById('raw_sort').addEventListener('click', function() {
      if (lastSort == 4)
        rawOrder = (rawOrder == 'asc') ? 'desc' : 'asc';
      else
        rawOrder = 'desc';
      lastSort = 4;
      sortTable(summary_table, lastSort, rawOrder, skip)
    });

    document.getElementById('untracked_sort').addEventListener('click', function() {
      if (lastSort == 5)
        untrackedOrder = (untrackedOrder == 'asc') ? 'desc' : 'asc';
      else
        untrackedOrder = 'desc';
      lastSort = 5;
      sortTable(summary_table, lastSort, untrackedOrder, skip)
    });

    document.getElementById('prime_sort').addEventListener('click', function() {
      if (lastSort == 6)
        primeOrder = (primeOrder == 'asc') ? 'desc' : 'asc';
      else
        primeOrder = 'desc';
      lastSort = 6;
      sortTable(summary_table, lastSort, primeOrder, skip)
    });

    document.getElementById('cyber_sort').addEventListener('click', function() {
      if (lastSort == 7)
        cyberOrder = (cyberOrder == 'asc') ? 'desc' : 'asc';
      else
        cyberOrder = 'desc';
      lastSort = 7;
      sortTable(summary_table, lastSort, cyberOrder, skip)
    });

    document.getElementById('all_sort').addEventListener('click', function() {
      if (lastSort == 8)
        allOrder = (allOrder == 'asc') ? 'desc' : 'asc';
      else
        allOrder = 'desc';
      lastSort = 8;
      sortTable(summary_table, lastSort, allOrder, skip)
    });

    document.getElementById('drops_sort').addEventListener('click', function() {
      if (lastSort == 9)
        dropsOrder = (strikeOrder == 'asc') ? 'desc' : 'asc';
      else
        dropsOrder = 'desc';
      lastSort = 9;
      sortTable(summary_table, lastSort, dropsOrder, skip)
    });

    document.getElementById('strike_sort').addEventListener('click', function() {
      if (lastSort == 10)
        strikeOrder = (strikeOrder == 'asc') ? 'desc' : 'asc';
      else
        strikeOrder = 'desc';
      lastSort = 10;
      sortTable(summary_table, lastSort, strikeOrder, skip)
    });

  }

  function toggleAverages(table) {
    document.getElementById('col-toggle').addEventListener('click', function() {
      var display, colSpan;
      // Set whether to show or hide
      if (this.classList.contains('col-expand')) {
        this.classList.add('col-collapse');
        this.classList.remove('col-expand');
        display = 'table-cell';
        colSpan = 10;
      } else {
        this.classList.add('col-expand');
        this.classList.remove('col-collapse');
        display = 'none';
        colSpan = 4;
      }

      var rows = Array.from(table.querySelectorAll('tr'));
      // Set the colspan for the first few rows
      for (var i = 0; i < skip-1; i++) {
        rows[i].children[0].colSpan = colSpan;
      }
      // Set the display for remaining rows
      rows = rows.slice(skip-1);
      rows.forEach(function(row) {
        for (var i = 3; i < 7; i++) {
          row.children[i].style.display = display;
        }
        row.children[8].style.display = display;
        row.children[9].style.display = display;
      });
    });
  }
})();

function getAverages(table, skip) {
  tracked = 0;
  raw = 0;
  untracked = 0;
  prime = 0;
  cyber = 0;
  all = 0;
  count = 0;
  var rows = Array.from(table.querySelectorAll('tr'));
  rows = rows.slice(skip);
  rows.forEach(function(row) {
    if ((row.style.display != 'none') && (row.children[1].children[0].innerText.trim() != 'Average')) {
      tracked += parseInt(row.children[2].innerText);
      raw += parseInt(row.children[3].innerText);
      untracked += parseInt(row.children[4].innerText);
      prime += parseInt(row.children[5].innerText);
      cyber += parseInt(row.children[6].innerText);
      all += parseInt(row.children[7].innerText);
      count += 1;
    }
  });

  document.getElementById('avg_tracked').innerText = Math.round(tracked / count);
  document.getElementById('avg_raw').innerText = Math.round(raw / count);
  document.getElementById('avg_untracked').innerText = Math.round(untracked / count);
  document.getElementById('avg_prime').innerText = Math.round(prime / count);
  document.getElementById('avg_cyber').innerText = Math.round(cyber / count);
  document.getElementById('avg_all').innerText = Math.round(all / count);
}

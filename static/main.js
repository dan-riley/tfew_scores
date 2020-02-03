var Main = (function() {

  var players;
  var summary_table;
  var playerOrder;
  var trackedOrder;
  var untrackedOrder;
  var primeOrder;
  var totalOrder;
  var lastSort = 0;

  document.addEventListener('DOMContentLoaded', function(event) {
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
      sortTable(lastSort, playerOrder)
    });

    document.getElementById('tracked_sort').addEventListener('click', function() {
      if (lastSort == 2)
        trackedOrder = (trackedOrder == 'asc') ? 'desc' : 'asc';
      else
        trackedOrder = 'desc';
      lastSort = 2;
      sortTable(lastSort, trackedOrder)
    });

    document.getElementById('untracked_sort').addEventListener('click', function() {
      if (lastSort == 3)
        untrackedOrder = (untrackedOrder == 'asc') ? 'desc' : 'asc';
      else
        untrackedOrder = 'desc';
      lastSort = 3;
      sortTable(lastSort, untrackedOrder)
    });

    document.getElementById('prime_sort').addEventListener('click', function() {
      if (lastSort == 4)
        primeOrder = (primeOrder == 'asc') ? 'desc' : 'asc';
      else
        primeOrder = 'desc';
      lastSort = 4;
      sortTable(lastSort, primeOrder)
    });

    document.getElementById('total_sort').addEventListener('click', function() {
      if (lastSort == 5)
        totalOrder = (totalOrder == 'asc') ? 'desc' : 'asc';
      else
        totalOrder = 'desc';
      lastSort = 5;
      sortTable(lastSort, totalOrder)
    });
  }

  function loadScoresTable() {
    for (player of players) {
      row = scores_left.insertRow();
      cell = row.insertCell(0);
      cell.innerHTML = player.order;
      cell = row.insertCell(1);
      cell.innerHTML = player.name;

      row = scores_right.insertRow();
      cell = row.insertCell(0);
      if (player.score)
        cell.innerHTML = player.score;
      else
        cell.innerHTML = '&nbsp;';
      cell.setAttribute('contenteditable', 'true');
      cell.id = player.name
    }

    addScores();
  }

  function sortScores(sorter, order) {
    // Update player scores with any changes
    for (player of players) {
      player.score = document.getElementById(player.name).innerHTML.trim();
    }

    // Sort
    players.sort(compareValues(sorter, order));

    //Remove all the rows except the title
    scores_left.getElementsByTagName('tbody')[0].innerHTML = scores_left.rows[0].innerHTML;
    scores_right.getElementsByTagName('tbody')[0].innerHTML = scores_right.rows[0].innerHTML;

    // Re-add the listeners and then rebuild the table
    addSortListeners();
    loadScoresTable();
  }

  function compareValuesSummary(a, b, order) {
    const comparison = a.localeCompare(b, undefined, {numeric: true});
    return ((order === 'desc') ? (comparison * -1) : comparison)
  }

  function sortTable(colnum, order) {
    let rows = Array.from(summary_table.querySelectorAll('tr'));
    rows = rows.slice(12);

    let qs = `td:nth-child(${colnum})`;

    rows.sort((r1, r2) => {
      let t1 = r1.querySelector(qs);
      let t2 = r2.querySelector(qs);

      return compareValuesSummary(t1.textContent, t2.textContent, order);
    });

    rows.forEach(row => summary_table.appendChild(row));
  }
})();

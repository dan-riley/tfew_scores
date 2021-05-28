var Ranker = (function() {

  var players;
  var summary_table;
  var playerOrder = 'asc';
  var allianceOrder = 'asc';
  var allOrder;
  var countOrder;
  var lastSort = 2;
  var skip = 7;

  document.addEventListener('DOMContentLoaded', function(event) {
    summary_table = document.getElementById('summary_table');
    // Initialize listeners
    addSortListeners();
    addZoomListeners(summary_table);

    // Setup min war input toggle
    toggleRows('min_wars_check', summary_table, skip, 3, 'False', 'getAveragesRanker', [summary_table, skip]);
    checkBox(document.getElementsByName('min_wars_check')[0]);
    addMinWarListener();

    // Get the players averages before sorting
    getAveragesRanker(summary_table, skip);

    // Sort by average, then alliance, then wars, then player (starts as player)
    triggerEvent(document.getElementById('count_sort'), 'click');
    triggerEvent(document.getElementById('alliance_sort'), 'click');
    triggerEvent(document.getElementById('avg_sort'), 'click');
  });

  function addMinWarListener() {
    document.getElementById('min_wars').addEventListener('change', function() {
      uncheckBox(document.getElementsByName('min_wars_check')[0]);
      min = this.value;
      var rows = Array.from(summary_table.querySelectorAll('tr'));
      rows = rows.slice(skip);
      rows.forEach(function(row) {
        if (row.children[1].innerText.trim() != 'Average') {
          count = parseInt(row.children[3].children[0].innerText);
          if (count >= min)
            row.children[3].children[1].value = 'True';
          else
            row.children[3].children[1].value = 'False';
        }
      });
      checkBox(document.getElementsByName('min_wars_check')[0]);
    });
  }

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

    document.getElementById('avg_sort').addEventListener('click', function() {
      if (lastSort == 3)
        allOrder = (allOrder == 'asc') ? 'desc' : 'asc';
      else
        allOrder = 'desc';
      lastSort = 3;
      sortTable(summary_table, lastSort, allOrder, skip)
    });

    document.getElementById('count_sort').addEventListener('click', function() {
      if (lastSort == 4)
        countOrder = (countOrder == 'asc') ? 'desc' : 'asc';
      else
        countOrder = 'desc';
      lastSort = 4;
      sortTable(summary_table, lastSort, countOrder, skip)
    });

    document.getElementById('alliance_sort').addEventListener('click', function() {
      if (lastSort == 5)
        allianceOrder = (allianceOrder == 'asc') ? 'desc' : 'asc';
      else
        allianceOrder = 'asc';
      lastSort = 5;
      sortTable(summary_table, lastSort, allianceOrder, skip)
    });
  }
})();

function getAveragesRanker(table, skip) {
  all = 0;
  count = 0;
  var rows = Array.from(table.querySelectorAll('tr'));
  rows = rows.slice(skip);
  rows.forEach(function(row) {
    if ((row.style.display != 'none') && (row.children[1].innerText.trim() != 'Average')) {
      all += parseInt(row.children[2].innerText);
      count += 1;
    }
  });

  document.getElementById('avg_all').innerText = Math.round(all / count);
}

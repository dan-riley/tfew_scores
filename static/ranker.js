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

    // Add reorg functions
    addReorgListener();
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

  function addReorgListener() {
    document.getElementsByName('reorganize')[0].addEventListener('click', function() {
      var avgs = [];
      avgs.oldT = [];
      avgs.newT = [];
      avgs.count = [];

      var ntable = document.getElementById('reorgTable');
      var rows = Array.from(summary_table.querySelectorAll('tr'));
      rows = rows.slice(skip);
      rows.forEach(function(row) {
        if ((row.style.display != 'none') && (row.children[1].innerText.trim() != 'Average')) {
          var newAlliance = "Sector 7";
          var count = parseInt(row.children[0].innerText.trim());
          if (count > 160) newAlliance = "";
          else if (count > 120) newAlliance = "S7 Omega";
          else if (count > 80) newAlliance = "Scorched Moon";
          else if (count > 40) newAlliance = "Scorched Earth";

          var avg = parseInt(row.children[2].innerText.trim());
          var oldAlliance = row.children[4].innerText.trim();
          if (!avgs.newT[newAlliance]) avgs.newT[newAlliance] = avg;
          else avgs.newT[newAlliance] += avg;
          if (!avgs.oldT[oldAlliance]) avgs.oldT[oldAlliance] = avg;
          else avgs.oldT[oldAlliance] += avg;
          if (!avgs.count[oldAlliance]) avgs.count[oldAlliance] = 1;
          else avgs.count[oldAlliance]++;

          var nrow = ntable.insertRow();
          for (i=0; i < 5; i++) {
            var ncell = nrow.insertCell();
            ncell.innerText = row.children[i].innerText.trim();
          }
          ncell = nrow.insertCell();
          ncell.innerText = newAlliance;
        }
      });
      document.getElementById('S7count').innerText = avgs.count['Sector 7'];
      document.getElementById('S7old').innerText = Math.round(avgs.oldT['Sector 7'] / avgs.count['Sector 7']);
      document.getElementById('S7new').innerText = Math.round(avgs.newT['Sector 7'] / 40);
      document.getElementById('SEcount').innerText = avgs.count['Scorched Earth'];
      document.getElementById('SEold').innerText = Math.round(avgs.oldT['Scorched Earth'] / avgs.count['Scorched Earth']);
      document.getElementById('SEnew').innerText = Math.round(avgs.newT['Scorched Earth'] / 40);
      document.getElementById('SMcount').innerText = avgs.count['Scorched Moon'];
      document.getElementById('SMold').innerText = Math.round(avgs.oldT['Scorched Moon'] / avgs.count['Scorched Moon']);
      document.getElementById('SMnew').innerText = Math.round(avgs.newT['Scorched Moon'] / 40);
      document.getElementById('SOcount').innerText = avgs.count['S7 Omega'];
      document.getElementById('SOold').innerText = Math.round(avgs.oldT['S7 Omega'] / avgs.count['S7 Omega']);
      document.getElementById('SOnew').innerText = Math.round(avgs.newT['S7 Omega'] / 40);
    }) ;
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

function download_table_as_csv(table_id, separator = ',') {
  // Select rows from table_id
  var rows = document.querySelectorAll('table#' + table_id + ' tr');
  // Construct csv
  var csv = [];
  for (var i = 0; i < rows.length; i++) {
    var row = [], cols = rows[i].querySelectorAll('td, th');
    for (var j = 0; j < cols.length; j++) {
      // Clean innertext to remove multiple spaces and jumpline (break csv)
      var data = cols[j].innerText.replace(/(\r\n|\n|\r)/gm, '').replace(/(\s\s)/gm, ' ')
      // Escape double-quote with double-double-quote (see https://stackoverflow.com/questions/17808511/properly-escape-a-double-quote-in-csv)
      data = data.replace(/"/g, '""');
        // Push escaped string
        row.push('"' + data + '"');
      }
    csv.push(row.join(separator));
  }
  var csv_string = csv.join('\n');
  // Download it
  var filename = 'export_' + table_id + '_' + new Date().toLocaleDateString() + '.csv';
  var link = document.createElement('a');
  link.style.display = 'none';
  link.setAttribute('target', '_blank');
  link.setAttribute('href', 'data:text/csv;charset=utf-8,' + encodeURIComponent(csv_string));
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

var OddsSimulator = (function() {

  var counts_table;
  var results_table;
  var starting_input_table;
  var num_sims_e;
  var num_crystals_e;
  var crystal_type_e;
  var crystal_type;
  var odds4_e;
  var odds3_e;
  var odds2_e;
  var add5_e;
  var avg_shards_e;
  var common_shards_e;
  var display_sims;
  var display_crystals;
  var clear_counts;
  var shards;

  document.addEventListener('DOMContentLoaded', function(event) {
    counts_table = document.getElementById('counts_table');
    results_table = document.getElementById('results_table');
    starting_input_table = document.getElementById('starting_input_table');
    num_sims_e = document.getElementById('num_sims');
    num_crystals_e = document.getElementById('num_crystals');
    crystal_type_e = document.getElementById('crystal_type');
    odds4_e = document.getElementById('odds4');
    odds3_e = document.getElementById('odds3');
    odds2_e = document.getElementById('odds2');
    add5_e = document.getElementById('add5');
    avg_shards_e = document.getElementById('avg_shards');
    common_shards_e = document.getElementById('common_shards');

    // Update the table with default values
    updateCalculator();

    // Listen to any input changes
    var inputs = document.querySelectorAll('input,select');
    for (var i = 0, len = inputs.length; i < len; i++) {
      inputs[i].addEventListener('change', function() {
        updateCalculator();
      });
    }

    document.getElementsByName('refresh')[0].addEventListener('click', function() {
      updateCalculator();
    });
  });

  function updateCalculator() {
    display_crystals = document.getElementsByName('crystals_check')[0].checked;
    display_sims = document.getElementsByName('sim_check')[0].checked;
    clear_counts = document.getElementsByName('clear_check')[0].checked;

    // Get the initial values
    var num_sims = num_sims_e.valueAsNumber;
    var num_crystals = num_crystals_e.valueAsNumber;
    crystal_type = crystal_type_e.value;
    if (crystal_type == 0)
      shards = Array(0,0,60,90,180);
    else
      shards = Array(0,0,2,20,180);
    var odds4 = odds4_e.valueAsNumber / 100;
    var odds3 = odds3_e.valueAsNumber / 100;
    var odds2 = 1 - odds4 - odds3;
    odds2_e.value = odds2 * 100;
    var add5 = add5_e.valueAsNumber;

    // Calculate the initial info
    if (clear_counts) counts_table.getElementsByTagName("tbody")[0].innerHTML = "";
    results_table.getElementsByTagName("tbody")[0].innerHTML = "";
    var nrow = 0;
    var counts = [];
    var ttstar = Array(0,0,0);
    var ttshards = Array(0,0,0);
    for (sim = 1; sim <= num_sims; sim++) {
      var tstar = Array(0,0,0);
      var tshards = Array(0,0,0);

      for (crystal = 1; crystal <= num_crystals; crystal++) {
        // Get the results of the pull
        var d = Math.random();
        var star = 2;
        if (d < odds4) star = 4;
        else if (d < odds3 + odds4) star = 3;
        // Totals
        tstar[star-2] += 1;
        tshards[star-2] += shards[star];

        // Display the results
        if (display_crystals) {
          var row = results_table.tBodies[0].insertRow(nrow++);
          var simCell = row.insertCell(0);
          simCell.innerHTML = parseInt(sim);
          var crystalCell = row.insertCell(1);
          crystalCell.innerHTML = parseInt(crystal);

          var starCell = row.insertCell(2);
          starCell.innerHTML = parseInt(star);

          var starCells = Array();
          starCells[0] = row.insertCell(3);
          starCells[1] = row.insertCell(4);
          starCells[2] = row.insertCell(5);
          starCells[star-2].innerHTML = parseInt(1);

          var shardsCells = Array();
          shardsCells[0] = row.insertCell(6);
          shardsCells[1] = row.insertCell(7);
          shardsCells[2] = row.insertCell(8);
          shardsCells[star-2].innerHTML = parseInt(shards[star]);
          if (crystal_type == 1) {
            shardsCells[2] = row.insertCell(9);
            shardsCells[2].innerHTML = parseInt(shards[star]);
          }
        }
      }

      // Totals
      var key = tstar[0] + ',' + tstar[1] + ',' + tstar[2];
      if (key in counts)
        counts[key] += 1;
      else
        counts[key] = 1;

      for (var i = 0; i < 3; i++) {
        ttstar[i] += tstar[i];
        ttshards[i] += tshards[i];
      }

      if (display_sims) {
        var row = results_table.tBodies[0].insertRow(nrow++);
        var tsimCell = row.insertCell(0);
        tsimCell.innerHTML = parseInt(sim);
        var tcrystalCell = row.insertCell(1);
        tcrystalCell.innerHTML = parseInt(num_crystals);
        var tstarCell = row.insertCell(2);

        var tstarCells = Array();
        tstarCells[0] = row.insertCell(3);
        tstarCells[0].innerHTML = parseInt(tstar[0]);
        tstarCells[1] = row.insertCell(4);
        tstarCells[1].innerHTML = parseInt(tstar[1]);
        tstarCells[2] = row.insertCell(5);
        tstarCells[2].innerHTML = parseInt(tstar[2]);

        var tshardsCells = Array();
        tshardsCells[0] = row.insertCell(6);
        tshardsCells[0].innerHTML = parseInt(tshards[0]);
        tshardsCells[1] = row.insertCell(7);
        tshardsCells[1].innerHTML = parseInt(tshards[1]);
        tshardsCells[2] = row.insertCell(8);
        tshardsCells[2].innerHTML = parseInt(tshards[2]);

        if (crystal_type == 1) {
          tshardsCells[2] = row.insertCell(9);
          tshardsCells[2].innerHTML = parseInt(tshards[0] + tshards[1] + tshards[2]);
        }
        row.style.fontWeight = 'bold';
      }
    }

    // Get averages
    var avgstar = Array(0,0,0);
    var avgshards = Array(0,0,0);
    for (i = 0; i < 3; i++) {
      avgstar[i] = ttstar[i] / num_sims;
      avgshards[i] = ttshards[i] / num_sims;
    }

    var row = counts_table.tBodies[0].insertRow(0);
    var summaryCell = row.insertCell(0);
    var bottext = ' bot';
    if (crystal_type == 1) bottext = ' combat bot';
    summaryCell.innerHTML = parseInt(num_sims) + ' simulations / ' + parseInt(num_crystals) + bottext + ' crystals'
    summaryCell.colSpan = 8;
    summaryCell.style.textAlign = 'center';
    row.style.fontWeight = 'bold';

    row = counts_table.tBodies[0].insertRow(1);
    var ttsimCell = row.insertCell(0);
    ttsimCell.innerHTML = 'Averages';

    var ttstarCells = Array();
    ttstarCells[0] = row.insertCell(1);
    ttstarCells[0].innerHTML = parseFloat(avgstar[0]).toFixed(1);
    ttstarCells[1] = row.insertCell(2);
    ttstarCells[1].innerHTML = parseFloat(avgstar[1]).toFixed(1);
    ttstarCells[2] = row.insertCell(3);
    ttstarCells[2].innerHTML = parseFloat(avgstar[2]).toFixed(1);

    var ttshardsCells = Array();
    ttshardsCells[0] = row.insertCell(4);
    ttshardsCells[0].innerHTML = parseFloat(avgshards[0]).toFixed(1);
    ttshardsCells[1] = row.insertCell(5);
    ttshardsCells[1].innerHTML = parseFloat(avgshards[1]).toFixed(1);
    ttshardsCells[2] = row.insertCell(6);
    ttshardsCells[2].innerHTML = parseFloat(avgshards[2]).toFixed(1);

    if (crystal_type == 1) {
      ttshardsCells[2] = row.insertCell(7);
      ttshardsCells[2].innerHTML = parseFloat(avgshards[0] + avgshards[1] + avgshards[2]).toFixed(1);
      avg_shards_e.innerHTML = parseFloat(avgshards[0] + avgshards[1] + avgshards[2] + add5).toFixed(1);
    } else
      avg_shards_e.innerHTML = parseFloat(avgshards[2] + add5).toFixed(1);

    row.style.fontWeight = 'bold';

    var scounts = Object.keys(counts).sort(function(a,b){return counts[b]-counts[a]}).map((key)=>({[key]: counts[key]}));

    for (var i = 0; i < 3; i++) {
      row = counts_table.tBodies[0].insertRow(i+2);
      ttsimCell = row.insertCell(0);
      ttsimCell.innerHTML = 'Common ' + parseInt(i+1) + ' (' + parseInt(scounts[i][Object.keys(scounts[i])]) + ')';
      cstar = Object.keys(scounts[i])[0].split(',');

      ttstarCells = Array();
      ttstarCells[0] = row.insertCell(1);
      ttstarCells[0].innerHTML = parseInt(cstar[0]);
      ttstarCells[1] = row.insertCell(2);
      ttstarCells[1].innerHTML = parseInt(cstar[1]);
      ttstarCells[2] = row.insertCell(3);
      ttstarCells[2].innerHTML = parseInt(cstar[2]);

      ttshardsCells = Array();
      ttshardsCells[0] = row.insertCell(4);
      ttshardsCells[0].innerHTML = parseInt(cstar[0] * shards[2]);
      ttshardsCells[1] = row.insertCell(5);
      ttshardsCells[1].innerHTML = parseInt(cstar[1] * shards[3]);
      ttshardsCells[2] = row.insertCell(6);
      ttshardsCells[2].innerHTML = parseInt(cstar[2] * shards[4]);

      if (crystal_type == 1) {
        ttshardsCells[2] = row.insertCell(7);
        ttshardsCells[2].innerHTML = parseInt(cstar[0] * shards[2] + cstar[1] * shards[3] + cstar[2] * shards[4]);
        if (i == 0)
          common_shards_e.innerHTML = parseInt(cstar[0] * shards[2] + cstar[1] * shards[3] + cstar[2] * shards[4] + add5);
      } else if (i == 0)
        common_shards_e.innerHTML = parseInt(cstar[2] * shards[4] + add5);

      row.style.fontWeight = 'bold';
    }
  }
})();

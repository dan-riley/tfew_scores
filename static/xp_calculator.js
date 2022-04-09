var XPCalculator = (function() {

  var results_table;
  var gmetal_results_table;
  var gold_results_table;
  var silver_results_table;
  var starting_input_table;
  var stars_e;
  var starting_level_e;
  var ending_level_e;
  var extra_xp_e;
  var min_zone_e;
  var xp_type_e;
  var bonus_e;
  var max_bots_e;
  var total_xp_e;
  var avg_level_e;
  var display_select_e;
  var xp;
  var zones;

  document.addEventListener('DOMContentLoaded', function(event) {
    results_table = document.getElementById('results_table');
    gmetal_results_table = document.getElementById('gmetal_results_table');
    gold_results_table = document.getElementById('gold_results_table');
    silver_results_table = document.getElementById('silver_results_table');
    starting_input_table = document.getElementById('starting_input_table');
    stars_e = document.getElementById('stars');
    starting_level_e = document.getElementById('starting_level');
    ending_level_e = document.getElementById('ending_level');
    extra_xp_e = document.getElementById('extra_xp');
    min_zone_e = document.getElementById('min_zone');
    xp_type_e = document.getElementById('xp_type');
    bonus_e = document.getElementById('bonus');
    max_bots_e = document.getElementById('max_bots');
    total_xp_e = document.getElementById('total_xp');
    avg_level_e = document.getElementById('avg_level');
    display_select_e = document.getElementById('display_select');

    // Load the data tables
    loadXP();
    loadZones();

    // Update the table with default values
    updateCalculator();

    // Listen to any input changes
    var inputs = document.querySelectorAll('input,select');
    for (var i = 0, len = inputs.length; i < len; i++) {
      inputs[i].addEventListener('blur', function() {
        updateCalculator();
      });
    }
  });

  function loadXP() {
    var star3 = Array(120,150,180,220,270,320,380,450,520,0,
                      830,1100,1200,1400,1600,1900,2100,2300,2700,0,
                      4600,5700,6900,8200,9600,11000,12000,14000,16000,0,
                      22000,26000,31000,36000,42000,48000,55000,63000,71000,0,
                      100000,130000,160000,210000,270000,340000,420000,540000,670000,0,
                      1100000,1500000,2100000,2800000,3800000,5100000,7000000,9000000,13000000,0,
                      0,0,0,0,0);
    var star4 = Array(150,180,220,270,330,390,460,540,630,0,
                      1000,1200,1400,1700,1900,2200,2500,2900,3200,0,
                      5500,6900,8300,9900,13000,14000,15000,17000,19000,0,
                      27000,31000,37000,43000,50000,58000,66000,75000,85000,0,
                      120000,150000,200000,250000,320000,400000,510000,640000,810000,0,
                      1300000,1800000,2500000,3400000,4600000,6200000,8400000,11000000,15000000,0,
                      20000000,25000000,30000000,41000000,0);
    var star5 = Array(170,210,260,320,390,450,540,630,740,0,
                      1100,1400,1700,2000,2200,2500,2900,3500,3700,0,
                      6500,8000,9700,11600,16400,17000,18000,20000,22000,0,
                      31000,37000,43000,50000,58000,67000,77000,88000,100000,0,
                      140000,180000,230000,290000,370000,470000,600000,750000,940000,0,
                      1600000,2100000,2900000,4000000,5400000,7300000,9800000,13000000,18000000,0,
                      23000000,29000000,35000000,48000000,0);

    xp = Array(star3, star4, star5);
  }

  function loadZones() {
    // 0 = Super, 1 = Triple, 2 = Normal
    zones = Array();
    zones[0] = Array(0,0,0,0,0,0,0,0,0,0,0,80000,105000,160000,240000,480000);
    zones[1] = Array(0,0,0,0,0,0,0,0,0,0,0,56000,80000,120000,160000,320000);
    zones[2] = Array(0,0,0,0,0,0,0,0,0,0,0,18000,25000,40000,56000,120000);
  }

  function updateCalculator() {
    // Get the initial values
    var stars = stars_e.value;
    var starting_level = starting_level_e.valueAsNumber;
    var ending_level = ending_level_e.valueAsNumber;
    var extra_xp = extra_xp_e.valueAsNumber;
    var min_zone = min_zone_e.valueAsNumber;
    var xp_type = xp_type_e.value;
    var bonus = bonus_e.value;
    var max_bots = max_bots_e.value;
    var display_select = display_select_e.value;

    // Calculate the initial info
    var total_xp = extra_xp;
    for (l = starting_level; l < ending_level; l++) {
      total_xp += xp[stars][l-1];
    }
    var avg_level = Math.round((ending_level - starting_level) * 0.7) + starting_level;

    // Display the initial info
    total_xp_e.innerHTML = total_xp.toLocaleString();
    avg_level_e.innerHTML = avg_level;

    results_table.getElementsByTagName("tbody")[0].innerHTML = "";
    gmetal_results_table.getElementsByTagName("tbody")[0].innerHTML = "";
    gold_results_table.getElementsByTagName("tbody")[0].innerHTML = "";
    silver_results_table.getElementsByTagName("tbody")[0].innerHTML = "";
    for (mult = 1; mult <= 2.5; mult+=0.5) {
      for (zone = min_zone; zone <= 15; zone++) {
        // Build the results
        var r = zone - min_zone;
        var row;
        if (mult == 2.5) row = gmetal_results_table.tBodies[0].insertRow(r);
        else if (mult == 2) row = gold_results_table.tBodies[0].insertRow(r);
        else if (mult == 1.5) row = silver_results_table.tBodies[0].insertRow(r);
        else row = results_table.tBodies[0].insertRow(r);
        var zoneCell = row.insertCell(0);
        zoneCell.innerHTML = parseInt(zone);

        // XP for a single bot in this zone
        var xp_max = zones[xp_type][zone] * mult * bonus;
        // Average coins based on the average level battled
        var coins = Math.round(0.68 * (avg_level) - 1);

        var bot = Array();
        for (b = 1; b <= 8; b++) {
          bot[b] = Object();
          // Create the cell
          bot[b]['cell'] = row.insertCell(b);
          bot[b]['xp'] = Math.round(xp_max / b);
          // Calculate number of battles
          bot[b]['battles'] = Math.ceil(total_xp / bot[b].xp);
          // Calculate approximate number of coins
          bot[b]['coins'] = (bot[b].battles > 45) ? ((bot[b].battles - 45) * coins) : (bot[b].battles - 1) * coins;
          // Write to the table
          if (display_select == 'battles') {
            bot[b].cell.innerHTML = bot[b].battles.toLocaleString();
            bot[b].cell.title = 'XP: ' + bot[b].xp.toLocaleString() + ', Fuel: ' + (bot[b].battles * 5).toLocaleString() + ', Coins: ' + bot[b].coins.toLocaleString();
          } else if (display_select == 'xp') {
            bot[b].cell.innerHTML = bot[b].xp.toLocaleString();
            bot[b].cell.title = 'Battles: ' + bot[b].battles.toLocaleString() + ', Fuel: ' + (bot[b].battles * 5).toLocaleString() + ', Coins: ' + bot[b].coins.toLocaleString();
          } else if (display_select == 'coins') {
            bot[b].cell.innerHTML = bot[b].coins.toLocaleString();
            bot[b].cell.title = 'Battles: ' + bot[b].battles.toLocaleString() + ', XP: ' + bot[b].xp.toLocaleString() + ', Fuel: ' + (bot[b].battles * 5).toLocaleString();
          }
        }

        if ((zone == 12) || (zone == 13)) bot[1].cell.style.fontWeight = 'bold';
        if ((zone == 13) || (zone == 14)) bot[2].cell.style.fontWeight = 'bold';
        if (zone == 15) {
          bot[3].cell.style.fontWeight = 'bold';
          bot[8].cell.style.fontWeight = 'bold';
        }
      }

      var rows;
      if (mult == 2.5) rows = gmetal_results_table.rows;
      else if (mult == 2) rows = gold_results_table.rows;
      else if (mult == 1.5) rows = silver_results_table.rows;
      else rows = results_table.rows;

      // Hide the column if it's above the max set
      for (let row of rows) {
        for (let col of row.children) {
          if ((col.cellIndex > max_bots) && (col.cellIndex != 8)) {
            col.style.display = 'none';
          } else {
            col.style.display = 'table-cell';
          }
        }
      }

    }
  }
})();

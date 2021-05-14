var BundleCalculator = (function() {

  var coins_table;
  var starting_input_table;
  var bundle_input_table;
  var total_points_e;
  var total_hours_e;
  var points_per_e;
  var loss_rate_e;
  var starting_fuel_e;
  var starting_coins_e;
  var total_battles_e;
  var free_battles_e;
  var remaining_battles_e;
  var remaining_fuel_e;
  var bots_coins_e;
  var bundle_sets;

  document.addEventListener('DOMContentLoaded', function(event) {
    coins_table = document.getElementById('coins_table');
    starting_input_table = document.getElementById('starting_input_table');
    bundle_input_table = document.getElementById('bundle_input_table');
    total_points_e = document.getElementById('total_points');
    total_hours_e = document.getElementById('total_hours');
    points_per_e = document.getElementById('points_per');
    loss_rate_e = document.getElementById('loss_rate');
    starting_fuel_e = document.getElementById('starting_fuel');
    starting_coins_e = document.getElementById('starting_coins');
    total_battles_e = document.getElementById('total_battles');
    free_battles_e = document.getElementById('free_battles');
    remaining_battles_e = document.getElementById('remaining_battles');
    remaining_fuel_e = document.getElementById('remaining_fuel');
    bots_coins_e = document.getElementById('bots_coins');
    bundle_sets = document.querySelectorAll('[name^="bundle_"]');

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

  function updateCalculator() {
    // Get the initial values
    var total_points = total_points_e.valueAsNumber;
    var total_hours = total_hours_e.valueAsNumber;
    var points_per = points_per_e.valueAsNumber;
    var loss_rate = loss_rate_e.valueAsNumber;
    var starting_fuel = starting_fuel_e.valueAsNumber;
    var starting_coins = starting_coins_e.valueAsNumber;

    // Calculate the initial info
    var total_battles = Math.ceil((total_points / points_per) * (0.01 * loss_rate + 1));
    var free_battles = total_hours * 60 / 4 / 5 + Math.floor(starting_fuel / 5);
    var remaining_battles = total_battles - free_battles;
    var remaining_fuel = remaining_battles * 5;
    var bot1coins = (total_battles - total_hours) * 40; 
    var bot2coins = (total_battles - total_hours) * 40 * 2;
    var bot3coins = (total_battles - total_hours) * 40 * 3;

    // Display the initial info
    total_battles_e.innerHTML = total_battles;
    free_battles_e.innerHTML = free_battles;
    remaining_battles_e.innerHTML = remaining_battles;
    remaining_fuel_e.innerHTML = remaining_fuel;
    bots_coins_e.innerHTML = bot1coins.toLocaleString() + ' / ' + bot2coins.toLocaleString() + ' / ' + bot3coins.toLocaleString();

    // Get the bundle sets and totals
    var cost = Array();
    var fuel = Array();
    var coins = Array();
    for (set in bundle_sets) {
      if (bundle_sets[set].value) {
        var idx = bundle_sets[set].name.split('_');
        var val = bundle_sets[set].value.split('_');
        var i = idx[1];
        if (cost[i] === undefined) cost[i] = 0;
        if (fuel[i] === undefined) fuel[i] = 0;
        if (coins[i] === undefined) coins[i] = 0;
        cost[i] += parseInt(val[0]);
        fuel[i] += parseInt(val[1]);
        coins[i] += parseInt(val[2]);
      }
    }

    coins_table.getElementsByTagName("tbody")[0].innerHTML = "";
    for (i in cost) {
      // Display totals for each set of bundles
      total_e = document.getElementById('total_' + i);
      total_e.innerHTML = '$' + cost[i] + ': ' + fuel[i] + ' fuel, ' + coins[i].toLocaleString() + ' coins';

      // Build the results
      var row = coins_table.tBodies[0].insertRow(i);
      var setNumCell = row.insertCell(0);
      var coinsAvailableCell = row.insertCell(1);
      var fuelNeededCell = row.insertCell(2);
      var coinsNeededCell = row.insertCell(3);
      var bot1Cell = row.insertCell(4);
      var bot2Cell = row.insertCell(5);
      var bot3Cell = row.insertCell(6);

      var coinsAvailable = coins[i] + starting_coins;
      var fuelNeeded = remaining_fuel - fuel[i];
      if (fuelNeeded < 0) fuelNeeded = 0;
      var coinsNeeded = Math.ceil((fuelNeeded / 50) * 800);
      var bot1 = coinsNeeded + bot1coins;
      var bot2 = coinsNeeded + bot2coins;
      var bot3 = coinsNeeded + bot3coins;

      var bot1color = 'green';
      var bot2color = 'green';
      var bot3color = 'green';

      setNumCell.innerHTML = parseInt(i) + 1;
      coinsAvailableCell.innerHTML = coinsAvailable.toLocaleString();
      fuelNeededCell.innerHTML = fuelNeeded;
      coinsNeededCell.innerHTML = coinsNeeded.toLocaleString();
      bot1Cell.innerHTML = bot1.toLocaleString();
      bot2Cell.innerHTML = bot2.toLocaleString();
      bot3Cell.innerHTML = bot3.toLocaleString();
      bot1Cell.title = coinsAvailable - bot1;
      bot2Cell.title = coinsAvailable - bot2;
      bot3Cell.title = coinsAvailable - bot3;

      if (bot1 > coinsAvailable) bot1color = 'red';
      if (bot2 > coinsAvailable) bot2color = 'red';
      if (bot3 > coinsAvailable) bot3color = 'red';
    
      bot1Cell.style.color = bot1color;
      bot1Cell.style.fontWeight = 'bold';
      bot2Cell.style.color = bot2color;
      bot2Cell.style.fontWeight = 'bold';
      bot3Cell.style.color = bot3color;
      bot3Cell.style.fontWeight = 'bold';
    }
  }
})();

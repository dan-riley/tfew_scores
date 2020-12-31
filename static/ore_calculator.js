var OreCalculator = (function() {

  var results;
  var ore_table;
  var ore_input_table;
  var max_storage;
  var max_harvester;
  var current_storage;
  var current_harvester;
  var hours_till_use;
  var amount_to_use;

  document.addEventListener('DOMContentLoaded', function(event) {
    results = document.getElementById('results');
    ore_table = document.getElementById('ore_table');
    ore_input_table = document.getElementById('ore_input_table');
    max_storage = document.getElementById('max_storage');
    max_harvester = document.getElementById('max_harvester');
    current_storage = document.getElementById('current_storage');
    current_harvester = document.getElementById('current_harvester');
    hours_till_use = document.getElementById('hours_till_use');
    amount_to_use = document.getElementById('amount_to_use');

    // Update the table with default values
    updateCalculator();

    // Listen to any input changes
    var inputs = document.querySelectorAll('input[type="number"]');
    for (var i = 0, len = inputs.length; i < len; i++) {
      inputs[i].addEventListener('blur', function() {
        updateCalculator();
      });
    }
  });

  function updateCalculator() {
    // Get the initial values
    var hours_calc = hours_till_use.valueAsNumber;
    var amount = amount_to_use.valueAsNumber;
    var storage = current_storage.valueAsNumber;
    if (isNaN(storage)) storage = 0;
    var harvest = current_harvester.valueAsNumber;
    if (isNaN(harvest)) harvest = 0;
    var storage_purge = storage + harvest;
    if (storage_purge > max_storage.valueAsNumber){
      storage_purge = max_storage.valueAsNumber;
    }
    var harvest_purge = 0;

    ore_table.getElementsByTagName("tbody")[0].innerHTML = "";
    for (i = 0; i < 48; i++) {
      // Add the row
      var row = ore_table.tBodies[0].insertRow(i);
      var hoursCell = row.insertCell(0);
      var gainedCell = row.insertCell(1);
      var no_purgeCell = row.insertCell(2);
      var purgeCell = row.insertCell(3);

      hours = i+1;

      // Set the harvester rate
      if (max_harvester.valueAsNumber == 70) gained = 2;
      else gained = 1.6;

      // Include the used amount if this is the appropriate hour
      var used = 0;
      if (hours == hours_calc) {
        used = amount;
      }

      // Get the no purge values
      storage -= used;
      harvest += gained;
      color = 'black';
      if (harvest >= max_harvester.valueAsNumber) {
        harvest = max_harvester.valueAsNumber;
        color = 'red';
      }
      no_purge = storage + harvest;

      // Get the purge values
      storage_purge -= used;
      harvest_purge += gained;
      color_purge = 'black';
      if (harvest_purge >= max_harvester.valueAsNumber) {
        harvest_purge = max_harvester.valueAsNumber;
        color_purge = 'red';
      }
      purge = storage_purge + harvest_purge;

      // Write the row
      hoursCell.innerHTML = hours;
      gainedCell.innerHTML = Math.floor(hours * gained);
      no_purgeCell.innerHTML = Math.floor(no_purge);
      no_purgeCell.style.color = color;
      purgeCell.innerHTML = Math.floor(purge);
      purgeCell.style.color = color_purge;

      // Display a message for what to do
      if (hours == hours_calc) {
        if (purge >= no_purge) {
          results.innerHTML = 'You should purge your harvester!';
          results.style.fontWeight = 'bold';
          results.style.color = 'green';
        } else {
          results.innerHTML = 'You should wait!';
          results.style.fontWeight = 'bold';
          results.style.color = 'red';
        }
      }
    }
  }
})();

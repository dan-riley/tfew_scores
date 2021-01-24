var WarCalculator = (function() {

  var war_input_table;
  var scores;
  var low_scores;
  var our_total;
  var opp_total;
  var our_max;
  var opp_max;
  var enable_low;
  var low_els;

  var our = Array();
  var opp = Array();
  var our_low = Array();
  var opp_low = Array();

  document.addEventListener('DOMContentLoaded', function(event) {
    war_input_table = document.getElementById('war_input_table');
    scores = document.getElementById('scores');
    low_scores = document.getElementById('low_scores');
    our_total = document.getElementById('our_total');
    opp_total = document.getElementById('opp_total');
    our_max = document.getElementById('our_max');
    opp_max = document.getElementById('opp_max');
    low_els = document.getElementsByClassName('low');
    enable_low = false;

    initCalculator();
    updateCalculator();

    document.getElementById('enableLow').addEventListener('click', function() {
      enable_low = !enable_low;
      for (var i = 0; i < low_els.length; i++) {
        if (enable_low) {
          low_els[i].classList.remove('hide');
          this.innerHTML = "Disable Extra Players";
        } else {
          low_els[i].classList.add('hide');
          this.innerHTML = "Enable Extra Players";
        }
      }
      updateCalculator();
    })

    document.getElementById('addScore').addEventListener('click', function() {
      scores.append(createRow(scores.rows.length));
    })

    document.getElementById('addLow').addEventListener('click', function() {
      low_scores.append(createLow(low_scores.rows.length));
    })
  });

  function getPoints(row) {
    var max = 0;
    var baseMult = 0;
    var attemptMult = 0;
    for (var i in row.base) {
      if (row.base[i].firstChild.checked) {
        baseMult = row.base[i].firstChild.value;
      }
    }
    for (var i in row.attempt) {
      if (row.attempt[i].firstChild.checked) {
        attemptMult = row.attempt[i].firstChild.value;
      }
    }

    var baseMult2 = baseMult;
    while (baseMult && attemptMult && baseMult2 <= 5) {
      // Change attempts to max for later bases
      if (baseMult2 > baseMult)
        attemptMult = 3;
      // Add the normal mode points
      max += 5 * baseMult2 * attemptMult;
      // Add hard mode points for later bases, and if hard selected for current
      if (!row.mode.firstChild.checked || (baseMult2 > baseMult))
        max += 5 * baseMult2;
      baseMult2++;
    }

    return max;
  }

  function calcScore(max, arr, arr_low) {
    var scores = Array();
    var low_count = 0;
    if (enable_low) {
      // Find out how many "extra" players there are, and save those scores
      for (var i in arr_low) {
        if (arr_low[i].value) {
          low_count++;
          scores.push(parseInt(arr_low[i].value));
        }
      }
    }

    for (var i in arr) {
      arr[i].score = getPoints(arr[i]);
      if (arr[i].score) {
        // Have to add in the current score for comparison with the other low scores later
        var cur_score = (low_count && arr[i].cur_score.value) ? parseInt(arr[i].cur_score.value) : 0;
        arr[i].score += cur_score;
        max += arr[i].score;
        // If this isn't a low score currently, need to remove the current score from max
        if (!arr[i].low.firstChild.checked)
          max -= cur_score;
        scores.push(arr[i].score);
      }
    }

    if (low_count && ((scores.length - low_count) >= low_count)) {
      scores.sort(function(a,b){return a-b});
      // Remove the lowest N scores
      for (var i = 0; i < low_count; i++) {
        max -= scores[i];
      }
    }

    return max;
  }

  function updateCalculator() {
    var ourMax = (our_total.value) ? parseInt(our_total.value) : 0;
    var oppMax = (opp_total.value) ? parseInt(opp_total.value) : 0;

    // Update the max scores for each side
    ourMax = calcScore(ourMax, our, our_low);
    oppMax = calcScore(oppMax, opp, opp_low);

    // Display the scores
    our_max.innerHTML = ourMax;
    opp_max.innerHTML = oppMax;

    // Remove the classes
    our_max.classList.remove('win');
    our_max.classList.remove('loss');
    opp_max.classList.remove('win');
    opp_max.classList.remove('loss');

    // Add the appropriate classes
    if (ourMax > oppMax) {
      our_max.classList.add('win');
      opp_max.classList.add('loss');
    } else{
      our_max.classList.add('loss');
      opp_max.classList.add('win');
    }
  }

  function highlightBelow(label) {
    var name = label.firstChild.name;
    var value = label.firstChild.value;
    var checked = label.firstChild.checked;
    var labels = label.parentElement.children;

    // Highlight all related elements below the selected one
    for (var i in labels) {
      var check = labels[i].firstChild;
      if (check && check.name == name) {
        // Clear the highlighting
        labels[i].classList.remove('calc-checked', 'calc-selected', 'calc-selected-loss');
        if (checked) {
          // Highlight this and all below
          if (check.value <= value)
            labels[i].classList.add('calc-checked');
          // Uncheck everything that isn't this one
          if (check.value != value)
            check.checked = false;
        }
      }

      if (checked && name.includes('base')) {
        // If the base was not checked, but now is, add the attempts and enable mode select
        if (!label.parentElement.classList.contains('active')) {
          if (check && check.name.includes('attempt') && (check.value == 3)) {
            // Check attempt 3 to highlight all
            check.click();
          } else if (check && check.name.includes('mode')) {
            // Enable the mode switch
            check.parentElement.classList.remove('hide');
            // Have to add the active class after the last element is processed!
            label.parentElement.classList.add('active');
          }
        }
      } else if (!checked && name.includes('base')) {
        // When unchecked, make sure all attempts are unchecked and unhighlighted, and hide mode
        if (check && check.name.includes('attempt')) {
          check.checked = false;
          labels[i].classList.remove('calc-checked');
        } else if (check && check.name.includes('mode')) {
            check.parentElement.classList.add('hide');
            label.parentElement.classList.remove('active');
        }
      }
    }

    // If it's the base select, make lighter similar to game
    // Have to do this after above loop since we clear the classes
    if (checked && name.includes('base')) {
      label.classList.add('calc-selected');
      var scoreMult = value - 1;
      var score = 0;
      while (scoreMult > 0) {
        score += 5 * scoreMult * 3 + 5 * scoreMult;
        scoreMult--;
      }
      label.parentElement.lastChild.value = score;
    }

    // Need to go back after to check if there's a loss so we can highlight base like game
    var base;
    for (var i in labels) {
      var check = labels[i].firstChild;
      if (check && check.name.includes('base') && check.checked) {
        base = check;
        base.parentElement.classList.remove('calc-selected-loss')
      }
      if (check && check.name.includes('attempt') && check.checked && check.value != 3)
        base.parentElement.classList.add('calc-selected-loss')
    }
  }

  function createCheck(name, value) {
    var label = document.createElement('label');
    var check = document.createElement('input');
    check.type = 'checkbox';
    check.name = name;
    check.value = value;
    check.classList.add('hide');
    label.appendChild(check);
    var text = '*';
    if (name.includes('base'))
      text = value;
    label.appendChild(document.createTextNode(text));

    label.addEventListener('change', function() {
      highlightBelow(this);
      updateCalculator();
    });

    return label;
  }

  function createModeCheck(name) {
    var label = document.createElement('label');
    var check = document.createElement('input');
    check.type = 'checkbox';
    check.name = name;
    check.classList.add('hide');
    label.appendChild(check);
    label.appendChild(document.createTextNode('H'));
    label.classList.add('hard-mode', 'hide');

    label.addEventListener('change', function() {
      if (this.firstChild.checked) {
        this.firstChild.nextSibling.nodeValue = 'N';
        this.classList.add('normal-mode');
        this.classList.remove('hard-mode');
      } else {
        this.firstChild.nextSibling.nodeValue = 'H';
        this.classList.remove('normal-mode');
        this.classList.add('hard-mode');
      }
      updateCalculator();
    });

    return label;
  }

  function createLowCheck(name) {
    var label = document.createElement('label');
    var check = document.createElement('input');
    check.type = 'checkbox';
    check.name = name;
    check.classList.add('hide');
    label.appendChild(check);
    label.appendChild(document.createTextNode('-'));
    label.classList.add('low', 'hide');

    label.addEventListener('change', function() {
      if (this.firstChild.checked) {
        this.firstChild.nextSibling.nodeValue = 'X';
        this.classList.add('calc-selected');
      } else {
        this.firstChild.nextSibling.nodeValue = '-';
        this.classList.remove('calc-selected');
      }
      updateCalculator();
    });

    return label;
  }

  function createInput(name) {
    var inp = document.createElement('input');
    inp.type = 'number';
    inp.name = name;
    inp.placeholder = 'Current Score';
    inp.classList.add('form-control', 'center')

    inp.addEventListener('change', function() {
      updateCalculator();
    });

    return inp;
  }

  function createRow(i) {
    var row = document.createElement('tr');
    var td1 = document.createElement('td');
    var td2 = document.createElement('td');
    var td3 = document.createElement('td');

    our[i] = Array();
    our[i].base = Array();
    our[i].attempt = Array();
    our[i].score = 0;
    // Create our bases
    for (var j = 0; j < 5; j++) {
      our[i].base[j] = createCheck('our_base_' + i, j + 1)
      td2.append(our[i].base[j]);
    }
    td2.append(document.createElement('br'));
    for (var j = 0; j < 3; j++) {
      our[i].attempt[j] = createCheck('our_attempt_' + i, j + 1)
      td2.append(our[i].attempt[j]);
    }
    our[i].mode = createModeCheck('our_mode_' + i);
    td2.append(our[i].mode);
    our[i].low = createLowCheck('our_low_score_' + i);
    td2.append(our[i].low);
    our[i].cur_score = createInput('our_cur_score_' + i);
    our[i].cur_score.classList.add('low', 'hide');
    td2.append(our[i].cur_score);

    opp[i] = Array();
    opp[i].base = Array();
    opp[i].attempt = Array();
    opp[i].score = 0;
    // Create opponent bases
    for (var j = 0; j < 5; j++) {
      opp[i].base[j] = createCheck('opp_base_' + i, j + 1)
      td3.append(opp[i].base[j]);
    }
    td3.append(document.createElement('br'));
    for (var j = 0; j < 3; j++) {
      opp[i].attempt[j] = createCheck('opp_attempt_' + i, j + 1)
      td3.append(opp[i].attempt[j]);
    }
    opp[i].mode = createModeCheck('opp_mode_' + i);
    td3.append(opp[i].mode);
    opp[i].low = createLowCheck('opp_low_score_' + i);
    td3.append(opp[i].low);
    opp[i].cur_score = createInput('opp_cur_score_' + i);
    opp[i].cur_score.classList.add('low', 'hide');
    td3.append(opp[i].cur_score);

    td1.innerHTML = i + 1;
    td2.classList.add('war_calc');
    td3.classList.add('war_calc');
    row.append(td1);
    row.append(td2);
    row.append(td3);

    return row;
  }

  function createLow(i) {
    var row = document.createElement('tr');
    var td1 = document.createElement('td');
    var td2 = document.createElement('td');
    var td3 = document.createElement('td');

    our_low[i] = createInput('our_low_' + i);
    td2.append(our_low[i]);

    opp_low[i] = createInput('opp_low_' + i);
    td3.append(opp_low[i]);

    td1.innerHTML = i + 1;
    row.append(td1);
    row.append(td2);
    row.append(td3);
    row.classList.add('low', 'hide');

    return row;
  }

  function initCalculator() {
    for (var i = 0; i < 5; i++) {
      scores.append(createRow(i));
    }
    for (var i = 0; i < 3; i++) {
      low_scores.append(createLow(i));
    }
  }
})();

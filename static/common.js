// Function to show alerts
function show_alert(message, alert) {
  alert_wrapper.innerHTML = `
    <div class="alert alert-${alert} alert-dismissible">
      <a href="#" class="close" data-dismiss="alert" aria-label="Close">&times;</a>
      <span>${message}</span>
    </div>
    `
}

// Form submission and responses
function initJSON(formNum, url) {
  if (window.location.search.indexOf('reload=success') > 0) {
    show_alert('Changes saved and page reloaded', 'success');
  }

  document.getElementById('submit').addEventListener('click', function() {
    var request = new XMLHttpRequest();
    request.addEventListener('load', function (e) {
        if (request.status == 200) {
          show_alert('Changes successfully saved', 'success');
          if (window.location.search.indexOf('reload=success') == -1) {
            window.location.search += "&reload=success";
          } else {
            location.reload();
          }
        } else {
          show_alert('Error submitting changes', 'danger');
        }
    });

    data = $(document.forms[formNum]).serializeObject();
    request.responseType = 'json';
    request.open('POST', url, true);
    request.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
    request.send(JSON.stringify(data));
  });
}

// Sorting algorithm
function compareValues(key, order = 'asc') {
  return function innerSort(a, b) {
    const comparison = a[key].localeCompare(b[key], undefined, {numeric: true});
    return ((order === 'desc') ? (comparison * -1) : comparison );
  };
}

function compareValuesFlask(a, b, order) {
  const comparison = a.localeCompare(b, undefined, {numeric: true});
  return ((order === 'desc') ? (comparison * -1) : comparison)
}

function sortTable(table, colnum, order, skip=1) {
  let rows = Array.from(table.querySelectorAll('tr'));

  // Set the sort icon on the table header
  var headers = document.querySelectorAll('[class*=sorted-]');
  [].forEach.call(headers, function(header) {
    header.classList.add('sorted-none');
    header.classList.remove('sorted-up');
    header.classList.remove('sorted-down');
  });
  var sorted = 'sorted-up';
  if (order == 'desc') sorted = 'sorted-down'
  let qs = `th:nth-child(${colnum})`;
  var sorter = rows[skip-1].querySelector(qs);
  sorter.classList.add(sorted);
  sorter.classList.remove('sorted-none');

  rows = rows.slice(skip);

  qs = `td:nth-child(${colnum})`;
  rows.sort((r1, r2) => {
    let t1 = r1.querySelector(qs);
    let t2 = r2.querySelector(qs);

    if ((t1.textContent.trim() == '') && (t2.textContent.trim() == ''))
      return compareValuesFlask(t1.children[0].value, t2.children[0].value, order);
    else
      return compareValuesFlask(t1.textContent, t2.textContent, order);
  });

  var rank = 1;
  rows.forEach(function(row) {
    if (row.style.display != 'none' && row.firstElementChild.classList.contains('rank')) {
      row.firstElementChild.innerText = rank++;
    }
    table.appendChild(row);
  });
}

// Autocomplete, based on https://www.w3schools.com/howto/howto_js_autocomplete.asp
function autocomplete(myinput, items) {
  var currentFocus;

  // Listen for user input
  myinput.addEventListener("input", function(e) {
    var a, b, i, val = this.value;
    closeAllLists();
    if (!val) { return false;}
    currentFocus = -1;
    // Results div
    a = document.createElement("DIV");
    a.setAttribute("id", this.id + "autocomplete-list");
    a.setAttribute("class", "autocomplete-items");
    this.parentNode.appendChild(a);

    for (i = 0; i < items.length; i++) {
      // Check first character of input and potential matches
      if (items[i].substr(0, val.length).toUpperCase() == val.toUpperCase()) {
        b = document.createElement("DIV");
        b.innerHTML = "<strong>" + items[i].substr(0, val.length) + "</strong>";
        b.innerHTML += items[i].substr(val.length);
        b.innerHTML += "<input type='hidden' value='" + items[i] + "'>";
        // Listen for a selection and move the selection to the input
        b.addEventListener("click", function(e) {
          myinput.value = this.getElementsByTagName("input")[0].value;
          closeAllLists();
        });
        a.appendChild(b);
      }
    }
  });

  // Manage keyboard navigation
  myinput.addEventListener("keydown", function(e) {
    var x = document.getElementById(this.id + "autocomplete-list");
    if (x) x = x.getElementsByTagName("div");
    if (e.keyCode == 40) {
      // Down arrow
      currentFocus++;
      addActive(x);
    } else if (e.keyCode == 38) {
      // Up arrow
      currentFocus--;
      addActive(x);
    } else if (e.keyCode == 13) {
      // Enter key
      e.preventDefault();
      if (currentFocus > -1) {
        if (x) x[currentFocus].click();
      }
    }
  });

  // Mark active item
  function addActive(x) {
    if (!x) return false;
    removeActive(x);
    if (currentFocus >= x.length) currentFocus = 0;
    if (currentFocus < 0) currentFocus = (x.length - 1);
    x[currentFocus].classList.add("autocomplete-active");
  }

  // Unmark active item
  function removeActive(x) {
    for (var i = 0; i < x.length; i++) {
      x[i].classList.remove("autocomplete-active");
    }
  }

  // Close the autocomplete list
  function closeAllLists(elmnt) {
    var x = document.getElementsByClassName("autocomplete-items");
    for (var i = 0; i < x.length; i++) {
      if (elmnt != x[i] && elmnt != myinput) {
        x[i].parentNode.removeChild(x[i]);
      }
    }
  }

  // Close the list if user clicks somewhere else
  document.addEventListener("click", function (e) {
    closeAllLists(e.target);
  });
}

function addZoomListeners(el) {
  el.style.zoom = 1.0;
  document.getElementById('zoom_reset').addEventListener('click', function() {
    el.style.zoom = 1.0;
  });

  document.getElementById('zoom_out').addEventListener('click', function() {
    el.style.zoom -= 0.05;
  });
}

function toggleRows(listen, table, skip, col, value, fnstring='', fnparams=[]) {
  // Toggle rows on and off, by looking at a hidden input on column=col equal to value
  // fnstring is optional function to run at the end, using array of params in fnparams
  document.getElementsByName(listen)[0].addEventListener('change', function() {
    var check = this;
    var rows = Array.from(table.querySelectorAll('tr'));
    rows = rows.slice(skip);
    rank = 1;
    rows.forEach(function(row) {
      if (check.checked) {
        if (row.children[col].children[1].value == value) {
          row.style.display = 'none';
        } else if (row.firstElementChild.classList.contains('rank')) {
          row.firstElementChild.innerText = rank++;
        }
      } else {
        row.style.display = 'table-row';
        if (row.firstElementChild.classList.contains('rank')) {
          row.firstElementChild.innerText = rank++;
        }
      }
      table.appendChild(row);
    });

    var fn = window[fnstring];
    if (typeof fn === "function") fn.apply(null, fnparams);
  });
}

function toggleColumns(listen, table, row, value) {
  // Toggle columns on and off, by looking at text in row=row equal to value
  // Uses class in a hidden input in the same cell
  document.getElementsByName(listen)[0].addEventListener('change', function() {
    let cols = table.rows[row].children;
    for (let col of cols) {
      if (col.innerText.trim() == value) {
        let className = col.children[0].value;
        let els = document.getElementsByClassName(className);
        for (let el of els) {
          if (this.checked) {
            el.style.display = 'none';
          } else {
            el.style.display = 'table-cell';
          }
        }
      }
    }
  });
}

function checkBox(element) {
  element.checked = 'checked';
  triggerEvent(element, 'change');
}

function triggerEvent(element, eventName) {
  var event = document.createEvent("HTMLEvents");
  event.initEvent(eventName, false, true);
  element.dispatchEvent(event);
}

// Function to show alerts
function show_alert(message, alert) {
  alert_wrapper.innerHTML = `
    <div class="alert alert-${alert} alert-dismissible">
      <a href="#" class="close" data-dismiss="alert" aria-label="Close">&times;</a>
      <span>${message}</span>
    </div>
    `
}

// Sorting algorithm
function compareValues(key, order = 'asc') {
  return function innerSort(a, b) {
    const comparison = a[key].localeCompare(b[key], undefined, {numeric: true});
    return ((order === 'desc') ? (comparison * -1) : comparison );
  };
}

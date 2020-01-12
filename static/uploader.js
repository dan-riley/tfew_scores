var Uploader = (function() {

  var progress, progress_wrapper, progress_status;
  var upload_btn, loading_btn, cancel_btn;
  var input, file_input_label;
  var alert_wrapper, scores_table;
  var players;

  document.addEventListener('DOMContentLoaded', function(event) {
    // Get a reference to the progress bar, wrapper & status label
    progress = document.getElementById('progress');
    progress_wrapper = document.getElementById('progress_wrapper');
    progress_status = document.getElementById('progress_status');

    // Get a reference to the 3 buttons
    upload_btn = document.getElementById('upload_btn');
    loading_btn = document.getElementById('loading_btn');
    cancel_btn = document.getElementById('cancel_btn');

    // Get a reference to the alert wrapper
    alert_wrapper = document.getElementById('alert_wrapper');
    scores_left = document.getElementById('scores_left');
    scores_right = document.getElementById('scores_right');

    input = document.getElementById('file_input');
    file_input_label = document.getElementById('file_input_label');

    // Function to update the input placeholder
    input.addEventListener('change', function() {
      file_input_label.innerText = input.files[0].name;
    });

    // Function to upload file
    upload_btn.addEventListener('click', function() {
      // Reject if the file input is empty & throw alert
      if (!input.value) {
        show_alert('No file selected', 'warning');
        return;
      }

      upload();
    });

    document.getElementById('load_scores').addEventListener('click', function() {
        var request = new XMLHttpRequest();
        request.responseType = 'json';

        request.addEventListener('load', function (e) {
            if (request.status == 200) {
                show_alert('Loaded previous scores', 'success');
                players = request.response;
                loadScoresTable();
            } else {
                show_alert('Error uploading file', 'danger');
            }
            reset();
        });
        request.open('POST', '/load_scores', true);
        request.send('');
    });

    document.getElementById('add_scores').addEventListener('click', function() {
      addScores();
    });

    addSortListeners();

  });

  function addSortListeners() {
    document.getElementById('order').addEventListener('click', function() {
      sortScores('order', 'asc');
    });

    document.getElementById('player').addEventListener('click', function() {
      sortScores('name', 'asc');
    });

    document.getElementById('score').addEventListener('click', function() {
      sortScores('score', 'desc');
    });
  }

  // Function to show alerts
  function show_alert(message, alert) {
    alert_wrapper.innerHTML = `
      <div class="alert alert-${alert} alert-dismissible">
        <a href="#" class="close" data-dismiss="alert" aria-label="Close">&times;</a>
        <span>${message}</span>
      </div>
      `
  }

  function upload() {
    // Create a new FormData instance
    var data = new FormData();

    // Create a XMLHTTPRequest instance
    var request = new XMLHttpRequest();

    // Set the response type
    request.responseType = 'json';

    // Clear any existing alerts
    alert_wrapper.innerHTML = '';

    // Disable the input during upload
    input.disabled = true;

    // Hide the upload button
    upload_btn.classList.add('d-none');

    // Show the loading button
    loading_btn.classList.remove('d-none');

    // Show the cancel button
    cancel_btn.classList.remove('d-none');

    // Show the progress bar
    progress_wrapper.classList.remove('d-none');

    // Get a reference to the file
    var file = input.files[0];

    // Get a reference to the filename
    var filename = file.name;

    // Get a reference to the filesize & set a cookie
    var filesize = file.size;
    document.cookie = `filesize=${filesize}`;

    // Append the file to the FormData instance
    data.append('file', file);

    // request progress handler
    request.upload.addEventListener('progress', function (e) {

      // Get the loaded amount and total filesize (bytes)
      var loaded = e.loaded;
      var total = e.total

        // Calculate percent uploaded
        var percent_complete = (loaded / total) * 100;

      // Update the progress text and progress bar
      progress.setAttribute('style', `width: ${Math.floor(percent_complete)}%`);
      progress_status.innerText = `${Math.floor(percent_complete)}% uploaded`;

    })

    // request load handler (transfer complete)
    request.addEventListener('load', function (e) {
      if (request.status == 200) {
        show_alert('Upload and processing complete!', 'success');

        var row, cell;
        players = request.response;
        loadScoresTable();
      } else {
        show_alert('Error uploading file', 'danger');
      }

      reset();
    });

    // request error handler
    request.addEventListener('error', function (e) {
      reset();
      show_alert('Error uploading file', 'warning');
    });

    // request abort handler
    request.addEventListener('abort', function (e) {
      reset();
      show_alert('Upload cancelled', 'primary');
    });

    // Open and send the request
    request.open('post', 'upload');
    request.send(data);

    cancel_btn.addEventListener('click', function () {
      request.abort();
    })
  }

  function addScores() {
    var score = 0;
    for (player of players) {
      newScore = parseInt(document.getElementById(player.name).innerHTML.trim());
      if (newScore) score += newScore;
    }

    document.getElementById('add_scores').innerHTML = 'Total (click to update): ' + score;
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

  function compareValues(key, order = 'asc') {
    return function innerSort(a, b) {
      const comparison = a[key].localeCompare(b[key], undefined, {numeric: true});
      return ((order === 'desc') ? (comparison * -1) : comparison );
    };
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

  // Function to reset the page
  function reset() {
    // Clear the input
    input.value = null;

    // Hide the cancel button
    cancel_btn.classList.add('d-none');

    // Reset the input element
    input.disabled = false;

    // Show the upload button
    upload_btn.classList.remove('d-none');

    // Hide the loading button
    loading_btn.classList.add('d-none');

    // Hide the progress bar
    progress_wrapper.classList.add('d-none');

    // Reset the progress bar state
    progress.setAttribute('style', "width: 0%");

    // Reset the input placeholder
    file_input_label.innerText = 'Select file';
  }
})();

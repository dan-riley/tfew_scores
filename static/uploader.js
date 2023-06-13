var Uploader = (function() {

  var progress, progress_wrapper, progress_status;
  var upload_btn, loading_btn, cancel_btn;
  var input, file_input_label;

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
  });

  function upload() {
    // Setup the data
    var data = new FormData();
    var request = new XMLHttpRequest();
    request.responseType = 'json';
    alert_wrapper.innerHTML = '';
    input.disabled = true;

    // Swap out some elements
    upload_btn.classList.add('hide');
    loading_btn.classList.remove('hide');
    cancel_btn.classList.remove('hide');
    progress_wrapper.classList.remove('hide');

    // Get the file
    var file = input.files[0];
    var filename = file.name;
    var filesize = file.size;
    document.cookie = `filesize=${filesize}`;

    // Append the file and alliance_id to the data for upload
    data.append('file', file);
    data.append('alliance_id', document.getElementById('alliance_id').value);

    // Show the user the progress
    request.upload.addEventListener('progress', function (e) {
      // Get the loaded amount and total filesize (bytes)
      var loaded = e.loaded;
      var total = e.total

      // Calculate percent uploaded
      var percent_complete = (loaded / total) * 100;

      // Update the progress text and progress bar
      progress.setAttribute('style', `width: ${Math.floor(percent_complete)}%`);
      progress_status.innerText = `${Math.floor(percent_complete)}% uploaded`;

      // When upload is complete, change the text so user knows it's processing now
      if (percent_complete == 100.0) loading_btn.innerHTML = 'Processing';
    });

    // Process the return data
    request.addEventListener('load', function (e) {
      if (request.status == 200) {
        show_alert('Upload and processing complete!', 'success');

        // Build the debug data
        document.getElementById('debug_btn').classList.remove('hide');
        document.getElementById('debug_body').innerHTML = '<b>Unmatched:</b><br />' + request.response[2].replace(/\n/g, '<br />') + '<br /><br /><b>Matched:</b><br />' + request.response[1].replace(/\n/g, '<br />');

        // Update the score table
        updateAIScores(request.response[0]);
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

  function updateAIScores(aiplayers) {
    var player, porder;
    for (aiplayer of aiplayers) {
      // Update the score and AI order for each player
      player = document.getElementsByName('players[' + aiplayer.id.toString() + '][score]')[0];
      porder = document.getElementsByName('players[' + aiplayer.id.toString() + '][airank]')[0];
      if (!player) {
        // If the player wasn't in the main table they must be a missing player
        player = document.getElementsByName('missing_players[' + aiplayer.id.toString() + '][score]')[0];
        porder = document.getElementsByName('missing_players[' + aiplayer.id.toString() + '][airank]')[0];
        // Unhide the player in case it wasn't already expanded
        player.parentElement.parentElement.classList.remove('collapse');
      }
      // Set the score in the input
      player.value = aiplayer.score;
      // Set the AI order in the hidden input and display it
      if (aiplayer.order != '99'){
        porder.value = aiplayer.order;
        document.getElementById('airank[' + aiplayer.id.toString() + ']').innerHTML = aiplayer.order;
      }
    }

    // Sort the table and trigger the totalizer with the last player
    triggerEvent(document.getElementById('ai_sort'), 'click');
    triggerEvent(player, 'blur');

    // Remove the missing players button as it won't be needed but gets re-added by sort
    missingRow = document.getElementById('missingPlayersButtonRow');
    if (missingRow)
      missingRow.parentNode.removeChild(missingRow);
  }

  function reset() {
    // Reset the buttons and inputs to the state before processing started
    input.value = null;
    input.disabled = false;

    upload_btn.classList.remove('hide');
    cancel_btn.classList.add('hide');
    loading_btn.classList.add('hide');
    loading_btn.innerHTML = 'Uploading...';
    progress_wrapper.classList.add('hide');

    progress.setAttribute('style', "width: 0%");
    file_input_label.innerText = 'Select file';
  }
})();

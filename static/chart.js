// Google Charts for data visualization
function loadChart(chartType) {
  document.getElementById('chart_div').style.display = 'block';
  document.getElementById('close_chart').style.display = 'block';

  google.charts.load('current', {'packages':['corechart']});
  google.charts.setOnLoadCallback(drawChart);

  function drawChart() {
    var data = new google.visualization.DataTable(spreadsJSON);
    var chart = new google.visualization.ScatterChart(document.getElementById('chart_div'));
    chart.draw(data, spreadsOptions);
  }
}

function closeChart() {
  document.getElementById('chart_div').style.display = 'none';
  document.getElementById('close_chart').style.display = 'none';
}

function buildChart(mydiv, mydataFunction, options, type) {
  google.charts.load('current', {'packages':['corechart']});
  google.charts.setOnLoadCallback(drawChart);

  function drawChart() {
    var data = window[mydataFunction]();

    var div = document.getElementById(mydiv);
    switch (type) {
      case 'line':
        var chart = new google.visualization.LineChart(div);
        break;

      case 'bar':
        var chart = new google.visualization.BarChart(div);
        break;

      case 'scatter':
        var chart = new google.visualization.ScatterChart(div);
        break;
    }

    chart.draw(data, options);
  }
}

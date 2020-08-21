var Issues = (function() {

  var issues_table;
  var idOrder;
  var commpleteOrder;
  var requesterOrder;
  var issueOrder;
  var commentsOrder;
  var lastSort = 0;

  document.addEventListener('DOMContentLoaded', function(event) {
    issues_table = document.getElementById('issues_table');
    addSortListeners();
    toggleRows('complete_toggle', issues_table, 1, 1, 'True');
  });

  function addSortListeners() {
    document.getElementById('id_sort').addEventListener('click', function() {
      if (lastSort == 1)
        idOrder = (idOrder == 'asc') ? 'desc' : 'asc';
      else
        idOrder = 'asc';
      lastSort = 1;
      sortTable(issues_table, lastSort, idOrder)
    });

    document.getElementById('complete_sort').addEventListener('click', function() {
      if (lastSort == 2)
        completeOrder = (completeOrder == 'asc') ? 'desc' : 'asc';
      else
        completeOrder = 'asc';
      lastSort = 2;
      sortTable(issues_table, lastSort, completeOrder)
    });

    document.getElementById('requester_sort').addEventListener('click', function() {
      if (lastSort == 3)
        requesterOrder = (requesterOrder == 'asc') ? 'desc' : 'asc';
      else
        requesterOrder = 'asc';
      lastSort = 3;
      sortTable(issues_table, lastSort, requesterOrder)
    });

    document.getElementById('issue_sort').addEventListener('click', function() {
      if (lastSort == 4)
        issueOrder = (issueOrder == 'asc') ? 'desc' : 'asc';
      else
        issueOrder = 'asc';
      lastSort = 4;
      sortTable(issues_table, lastSort, issueOrder)
    });

    document.getElementById('comments_sort').addEventListener('click', function() {
      if (lastSort == 5)
        commentsOrder = (commentsOrder == 'asc') ? 'desc' : 'asc';
      else
        commentsOrder = 'asc';
      lastSort = 5;
      sortTable(issues_table, lastSort, commentsOrder)
    });
  }
})();

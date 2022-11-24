var Donator = (function() {

  var amount;

  document.addEventListener('DOMContentLoaded', function(event) {
    amount = document.getElementsByName('amount')[0];
    var amount5 = document.getElementsByName('amount5')[0];
    var amount10 = document.getElementsByName('amount10')[0];
    var amount20 = document.getElementsByName('amount20')[0];

    addButton(amount5, '5.00');
    addButton(amount10, '10.00');
    addButton(amount20, '20.00');

    document.getElementsByName('CPToggleCheck')[0].addEventListener('click', function() {
      cpinput = document.getElementById('CPinput')
      cplabel = document.getElementById('CPlabel')
      if (this.checked) {
        cpinput.style.display = 'flex';
        cplabel.style.display = 'none'
      } else {
        cpinput.style.display = 'none';
        cplabel.style.display = 'inline-block'
      }
    });
  });

  function addButton(btn, value) {
    btn.addEventListener('click', function() {
      amount.value = value;
    })
  }
})();

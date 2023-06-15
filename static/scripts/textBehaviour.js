var tickerInput = document.getElementById('tickerInput');
document.addEventListener('keydown', function(event) {
  tickerInput.focus();
});
var tickerInput = document.getElementById('tickerInput');
tickerInput.addEventListener('input', function() {
    this.value = this.value.toUpperCase();
});

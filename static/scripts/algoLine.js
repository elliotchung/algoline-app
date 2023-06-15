var lineseries = [];

function getRandomColor() {
  const forbiddenColors = ['#26a69a', '#ef5350']; // Red and green
  const letters = '0123456789ABCDEF';
  let color;
  
  do {
    color = '#';
    for (let i = 0; i < 6; i++) {
      color += letters[Math.floor(Math.random() * 16)];
    }
  } while (forbiddenColors.includes(color));
  
  return color;
}

function handleCheckboxChange() {
  var checkbox = document.getElementById('myCheckbox');
  if (checkbox.checked) {
    // Code to execute when checkbox is checked
    var mylowElement = document.getElementById('my-low-trendlines');
    var lowTrendlineList = mylowElement.getAttribute('low-trendlines-data-list');
    const lowTrendlineListArray = JSON.parse(lowTrendlineList);

    var myhighElement = document.getElementById('my-high-trendlines');
    var highTrendlineList = myhighElement.getAttribute('high-trendlines-data-list');
    const highTrendlineListArray = JSON.parse(highTrendlineList);
    
    for (const data of lowTrendlineListArray) {
      var lineSeries = chart2.addLineSeries({ color: getRandomColor(), lineWidth: 0.9, crosshairMarkerVisible: false, priceLineVisible: false });
      lineSeries.setData(data);
      lineseries.push(lineSeries);
    }
    for (const data of highTrendlineListArray) {
      var lineSeries = chart2.addLineSeries({ color: getRandomColor(), lineWidth: 0.9, crosshairMarkerVisible: false, priceLineVisible: false });
      lineSeries.setData(data);
      lineseries.push(lineSeries);
    }
  } else {
    // Remove all trendlines
    for (const lineSeries of lineseries) {
      chart2.removeSeries(lineSeries);
    }
    lineseries = []; // Clear the array
  }
}

console.log('algoLine.js loaded');

handleCheckboxChange(); // Call the function once to draw the trendlines
// Create a select element for time interval options
const selectElement = document.createElement('select');
const options = [
  { label: '6 Months', value: 15552000 },
  { label: '1 Year', value: 31104000 },
  { label: '2 Years', value: 31104000 * 2 },
  { label: 'All', value: 31104000 * 10 }
];

// Add options to the select element
options.forEach(option => {
  const optionElement = document.createElement('option');
  optionElement.text = option.label;
  optionElement.value = option.value;
  selectElement.appendChild(optionElement);
});

// Add event listener to detect option selection
selectElement.addEventListener('change', function() {
  const selectedValue = parseInt(this.value, 10);
  const currentTimestamp = Math.floor(new Date().getTime() / 1000);
  const fromTimestamp = currentTimestamp - selectedValue;
  
  chart2.timeScale().setVisibleRange({
    from: fromTimestamp,
    to: currentTimestamp
  });
});

// Append the select element to the DOM
const containerElement = document.getElementById('timeIntervalSelectorDaily');
containerElement.appendChild(selectElement);

// Create a select element for time interval (5 min) options
const selectElement2 = document.createElement('select');
const options2 = [
  { label: '10 Days', value: 864000 },
  { label: '2 Days', value: 172800 },
  { label: 'All', value: 864000 * 10 }
];

// Add options to the select element
options2.forEach(option => {
  const optionElement = document.createElement('option');
  optionElement.text = option.label;
  optionElement.value = option.value;
  selectElement2.appendChild(optionElement);
}
);

// Add event listener to detect option selection
selectElement2.addEventListener('change', function() {
  const selectedValue = parseInt(this.value, 10);
  const currentTimestamp = Math.floor(new Date().getTime() / 1000);
  const fromTimestamp = currentTimestamp - selectedValue;
  
  chart.timeScale().setVisibleRange({
    from: fromTimestamp,
    to: currentTimestamp
  });
}
);

// Append the select element to the DOM
const containerElement2 = document.getElementById('timeIntervalSelectorFivemin');
containerElement2.appendChild(selectElement2);

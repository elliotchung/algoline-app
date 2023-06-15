const dailychartSize = document.getElementById('dailyChart');
const fiveminchartSize = document.getElementById('fiveminChart');


function setChartHeight() {
  const windowHeight = window.innerHeight;
  console.log(windowHeight);
  const chartHeight = windowHeight * 0.45; // Adjust the proportion as needed
  
  dailychartSize.style.height = `${chartHeight}px`;
  fiveminchartSize.style.height = `${chartHeight}px`;
}

// Set the initial height
setChartHeight();

// Update the height on window resize
window.addEventListener('resize', setChartHeight);


function setChartWidth() {
    const windowWidth = window.innerWidth;
    console.log(windowWidth);
    const chartWidth = windowWidth * 0.95; // Adjust the proportion as needed
    
    dailychartSize.style.width = `${chartWidth}px`;
    fiveminchartSize.style.width = `${chartWidth}px`;
    }

// Set the initial width
setChartWidth();

// Update the width on window resize
window.addEventListener('resize', setChartWidth);
console.log("chartSize.js loaded");

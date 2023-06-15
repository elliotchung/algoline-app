// Access the data from the HTML attribute
var myDataElement = document.getElementById('my-data');
var dataList = myDataElement.getAttribute('data-list');

// Convert the data into an array
var dataListArray = JSON.parse(dataList);

function timeToTz(originalTime, tzOffset) {
    const zonedDate = new Date(new Date(originalTime * 1000));
    const newDate = new Date(zonedDate.getTime() + tzOffset * 60 * 60 * 1000);
    return newDate.getTime() / 1000;
  }

const candleData = dataListArray.map(item => {
    const time = item[1];
    const timeString = new Date(time * 1000).toLocaleString();
    return {
        time: timeToTz(time, -4),
        open: item[2],
        high: item[3],
        low: item[4],
        close: item[5],
    }
});

const domElement = document.getElementById('fiveminChart');
const chart = LightweightCharts.createChart(domElement, chartProperties, chartOptions);

const candlestickSeries = chart.addCandlestickSeries({
    upColor: green, downColor: red, borderVisible: false,
    wickUpColor: green, wickDownColor: red,
});

candlestickSeries.setData(candleData);

const twoDays = 172800;
const tenDays = 864000;

chart.timeScale().setVisibleRange({
  from: currentTimestamp - tenDays,
  to: currentTimestamp,
});

console.log("fiveminChart.js loaded");
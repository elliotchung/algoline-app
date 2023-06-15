// Access the data from the HTML attribute
var myDailyDataElement = document.getElementById('my-daily-data');
var dailyDataList = myDailyDataElement.getAttribute('daily-data-list');

var dailyDataListArray = JSON.parse(dailyDataList);

function removeTime(originaldateTime) {
    const newDate = new Date(originaldateTime * 1000);
    const newDateNoTime = new Date(newDate.getFullYear(), newDate.getMonth(), newDate.getDate());
    return newDateNoTime.getTime() / 1000;
}

const dailyCandleData = dailyDataListArray.map(item => {
    return {
        time: item[0],
        open: item[1],
        high: item[2],
        low: item[3],
        close: item[4],
    }
});

const green = '#26a69a';
const red = '#ef5350';

const chartProperties = {
    autoSize: true,
      timeScale: {
          timeVisible: true,
          secondsVisible: false,
      },
  };

const chartOptions = { layout: { textColor: 'black', background: { type: 'solid', color: 'white' } } };



const domElement2 = document.getElementById('dailyChart');
const chart2 = LightweightCharts.createChart(domElement2, chartProperties, chartOptions);

const candlestickSeries2 = chart2.addCandlestickSeries({
  upColor: green, downColor: red, borderVisible: false,
  wickUpColor: green, wickDownColor: red,
});


candlestickSeries2.setData(dailyCandleData);

const currentDate = new Date();
const currentTimestamp = Math.floor(currentDate.getTime() / 1000);
const oneDay = 86400;
const oneWeek = 604800;
const oneMonth = 2592000;
const threeMonths = 7776000;
const sixMonths = 15552000;
const oneYear = 31104000;
const all = oneYear * 10;

chart2.timeScale().setVisibleRange({
  from: currentTimestamp - sixMonths,
  to: currentTimestamp,
});

console.log("dailyChart.js loaded");
var data = [
    [0, 12717],
    [0.05, 10857],
    [0.1, 10857],
    [0.15, 10857],
    [0.2, 982],
    [0.25, 800],
    [0.3, 700],
    [0.35, 500],
    [0.4, 100],
    [0.45, 6],
    [0.5, 6],
    [0.55, 6],
    [0.6, 6],
    [0.65, 6],
    [0.7, 6],
    [0.75, 6],
    [0.8, 6],
    [0.85, 6],
    [0.9, 6],
    [0.95, 6]


];
chart_container = "similarity_chart_container";
chart = anychart.column();
chart.container(chart_container);

// create a column series and set the data
var series = chart.column(data);



chart.background().fill('white');

// var state = series.normal();
// state.fill('#1481c0')

// x axix labels font setting
var xAxisLabels = chart.xAxis().labels();
xAxisLabels.fontFamily("vazir");

var yAxisLabels = chart.yAxis().labels();
yAxisLabels.fontFamily("vazir");

// Not allow labels overlapping
var xAxis = chart.xAxis();
xAxis.overlapMode("noOverlap");


// tooltip content font setting
var tooltip = chart.tooltip();
tooltip.fontFamily("vazir");
tooltip.titleFormat("تعداد یال‌ها: {%y}")

// tooltip title font setting
var title = chart.tooltip().title();
title.fontFamily("vazir");

chart.tooltip().hAlign('center').format("حداقل شباهت: {%x}");


// set all axis title 
var xAxis = chart.xAxis();
xAxis.title("آستانه شباهت");
xAxis.title().fontFamily('vazir');

var yAxis = chart.yAxis();
yAxis.title("تعداد یال‌ها");
yAxis.title().fontFamily('vazir');
chart.yAxis().labels().format("{%value}");

// xAxisLabels.rotation(-45)

// initiate drawing the chart
chart.draw();
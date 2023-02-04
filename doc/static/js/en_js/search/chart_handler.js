// create data


chart = anychart.bar();
chart.container(chart_container);
// create a column series and set the data
var series = chart.bar(data);



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

// tooltip title font setting
var title = chart.tooltip().title();
title.fontFamily("vazir");

chart.tooltip().hAlign('center').format("{%value}");


// set all axis title 


var yAxis = chart.yAxis();
yAxis.title("تعداد سند");
yAxis.title().fontFamily('vazir');
chart.yAxis().labels().format("{%value}");

chart.yScale().minimum(0);
chart.yScale().ticks().allowFractional(false);


// xAxisLabels.rotation(-45)

// initiate drawing the chart
chart.draw();
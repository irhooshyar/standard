// create data
var data = [
    ["ارتباطات و فناوری اطلاعات", 10],
    ["اقتصادی", 12],
    ["حقوقی-قضایی", 13],
    ["دفاعی-امنیتی", 10],
    ["سیاسی-اجتماعی", 9],
    ["علمی-نوآوری", 9],
    ["سیاست خارجی", 9],
    ["فرهنگی", 9],
    ["اختصاصی-تخصصی", 9],
];


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

// tooltip title font setting
var title = chart.tooltip().title();
title.fontFamily("vazir");

chart.tooltip().hAlign('center').format("%{%value}");


// set all axis title 
var xAxis = chart.xAxis();
xAxis.title("موضوع");
xAxis.title().fontFamily('vazir');

var yAxis = chart.yAxis();
yAxis.title("مشارکت");
yAxis.title().fontFamily('vazir');
chart.yAxis().labels().format("٪{%value}");




// xAxisLabels.rotation(-45)

// initiate drawing the chart
chart.draw();
function showTour(){
    introJs().setOptions({
    tooltipClass: 'customTooltip',
    nextLabel: 'بعدی',
    prevLabel: 'قبلی',
    doneLabel: 'اتمام',
    showProgress: false,
    steps: []
}).start();
}

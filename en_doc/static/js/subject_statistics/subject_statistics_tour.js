function showTour(){
    introJs().setOptions({
    tooltipClass: 'customTooltip',
    nextLabel: 'بعدی',
    prevLabel: 'قبلی',
    doneLabel: 'اتمام',
    showProgress: false,
    steps: [{
        element: document.querySelector('#start'),
        intro: "در این پنل می‌توانید با انتخاب کشور، اسناد آن کشور را از لحاظ موضوعات مختلف بررسی نمایید."
    }, {
        element: document.querySelector('#country'),
        intro: "مجموعه سند مورد نظر خود را از این قسمت انتخاب نمایید."
    }, {
        element: document.querySelector('#budget_results_tab'),
        intro: "در این تب اطلاعات نموداری مربوط به اسناد قوانین بودجه نشان داده شده است."
    }, {
        element: document.querySelector('#barname_results_tab'),
        intro: "در این تب اطلاعات نموداری مربوط به اسناد برنامه‌های توسعه نشان داده شده است."
    }]
}).start();


}

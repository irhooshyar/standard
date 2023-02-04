function showTour(){
    introJs().setOptions({
    tooltipClass: 'customTooltip',
    nextLabel: 'بعدی',
    prevLabel: 'قبلی',
    doneLabel: 'اتمام',
    showProgress: false,
    steps: [{
        element: document.querySelector('#start'),
        intro: "در این پنل می‌توانید روند تاثیر شعار رهبری را بر روی مجموعه قوانین مشاهده کنید"
    }, {
        element: document.querySelector('#country'),
        intro: "مجموعه سند مورد نظر خود را از این قسمت انتخاب نمایید."
    },{
        element: document.querySelector('#slogan'),
        intro: "شعار سال مورد نظر را به منظور بررسی میزان انعکاس آن در مجموعه قوانین، انتخاب کنید"
    },{
        element: document.querySelector('#document_search'),
        intro: "با کلیک بر روی این دکمه نمودار مورد نظر نمایش داده می‌شود."
    },{
        element: document.querySelector('#slogan-keyword'),
        intro: "در این قسمت می‌توانید کلیدواژه‌های استخراج شده از شعار رهبری به منظور جست‌وجو در مجموعه قوانین را مشاهده کنید."
    },{
        element: document.querySelector('#slogan_info_tab'),
        intro: "در این قسمت نمودارهای میزان انعکاس شعار رهبری در اسناد هر سال رسم می‌شود. "
    }]
}).start();


}

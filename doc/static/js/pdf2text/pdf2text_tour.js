function showTour(){
    introJs().setOptions({
    tooltipClass: 'customTooltip',
    nextLabel: 'بعدی',
    prevLabel: 'قبلی',
    doneLabel: 'اتمام',
    showProgress: false,
    steps: [{
        element: document.querySelector('#start'),
        intro: "این پنل برای تبدیل فایل‌های PDF به فایل‌های TXT ارائه شده‌است."
    }, {
        element: document.querySelector('#file_input_btn'),
        intro: " ابتدا با کلیک روی این قسمت «یک فایل زیپ» شامل فایل‌های PDF انتخاب نمایید."

    }, { element: document.querySelector('#LanguageSelect'),
        intro: "از این قسمت زبان‌ فایل‌های PDF را تعیین نمایید."
    },
        {
        element: document.querySelector('#process_btn'),
        intro: "با کلیک روی این گزینه، پردازش فایل‌های PDF آغاز می‌شود (پس از اتمام پردازش دکمه «دانلود نتایج» فعال می‌شود)."
    }, {
        element: document.querySelector('#download_button'),
        intro: "با کلیک روی این گزینه می‌توانید فایل‌های TXT ایجادشده را در قالب یک فایل زیپ دریافت نمایید."
    }]
}).start();


}

function showTour(){
    introJs().setOptions({
    tooltipClass: 'customTooltip',
    nextLabel: 'بعدی',
    prevLabel: 'قبلی',
    doneLabel: 'اتمام',
    showProgress: false,
    steps: [{
        element: document.querySelector('#start'),
        intro: "در این پنل با انتخاب کشور و موضوع سند، می‌توانید به تحلیل مراجع رسمی بپردازید."
    }, {
        element: document.querySelector('#country'),
        intro: "مجموعه سند مورد نظر خود را از این قسمت انتخاب نمایید."
    }, {
        element: document.querySelector('.multi-select-container'),
        intro: "موضوعات مورد نظر خود را انتخاب نمایید."
    }, {
        element: document.querySelector('#document_search'),
        intro: "با فشردن کلید نمایش می‌توانید اسناد مرتبط را به همراه مراجع رسمی مشاهده نمایید."
    },{
        element: document.querySelector('#result_doc'),
        intro: "در این تب می‌توانید لیست اسناد یافت‌شده را به همراه موضوع سند و مرجع رسمی به‌کار رفته در آن، مشاهده نمایید."
    },{
        element: document.querySelector('#ExportExcel'),
        intro: "با کلیک روی این گزینه امکان دانلود اسامی و اطلاعات جانبی مربوط به اسناد حاصل از جستجو را خواهید داشت."

    },{
        element: document.querySelector('#DownloadBtn'),
        intro: "با کلیک روی این گزینه امکان دانلود اسناد حاصل از جستجو را خواهید داشت."

    }]
}).start();


}

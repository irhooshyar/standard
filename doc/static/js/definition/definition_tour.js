function showTour(){
    introJs().setOptions({
    tooltipClass: 'customTooltip',
    nextLabel: 'بعدی',
    prevLabel: 'قبلی',
    doneLabel: 'اتمام',
    showProgress: false,
    steps: [{
        element: document.querySelector('#start'),
        intro: "در این پنل با انتخاب کشور و موضوع سند می‌توانید کلیدواژگان و تعاریف آن‌ها در اسناد مختلف را مشاهده نمایید."
    }, {
        element: document.querySelector('#country'),
        intro: "مجموعه سند مورد نظر خود را از این قسمت انتخاب نمایید."
    }, {
        element: document.querySelector('.multi-select-container'),
        intro: "موضوع مورد نظر خود را انتخاب نمایید."
    }, {
        element: document.querySelector('#document_search'),
        intro: "با فشردن کلید نمایش می‌توانیداطلاعات مربوط به واژگان و تعاریف آن‌ها را در اسناد مختلف مشاهده نمایید."
    },{
        element: document.querySelector('#keywords_extraction_tab'),
        intro: "در این تب می‌توانید اطلاعات مربوط به کلیدواژه، اسناد حاوی آن کلیدواژه و تعاریف آن را مشاهده نمایید."
    }, {
        element: document.querySelector('#keywords_chart_tab'),
        intro: "در این تب می‌توانید تعداد اسناد حاوی هر کلیدواژه را بر روی نمودار مشاهده نمایید. با کلیک بر روی هر ستون نمودار می‌توانید تعریف آن کلید واژه را به تفکیک سند مشاهده نمایید."
    }, {
        element: document.querySelector('#keywords_graph_tab'),
        intro: "در این تب می‌توانید گراف واژگان را برای هر سند مشاهده نمایید. با کلیک بر روی هر یال تعریف کلید واژه قابل مشاهده است."
    }, {
        element: document.querySelector('#ExportExcel'),
        intro: "برای دانلود کلیدواژگان و اطلاعات جانبی آن‌ها در قالب اکسل، روی این گزینه کلیک نمایید"

    },{
        element: document.querySelector('#DownloadBtn'),
        intro: "برای دانلود کلیدواژگان و اطلاعات جانبی آن‌ها، روی این گزینه کلیک نمایید"

    }]
}).start();


}

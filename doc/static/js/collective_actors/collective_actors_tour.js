function showTour(){
    introJs().setOptions({
    tooltipClass: 'customTooltip',
    nextLabel: 'بعدی',
    prevLabel: 'قبلی',
    doneLabel: 'اتمام',
    showProgress: false,
    steps: [{
        element: document.querySelector('#start'),
        intro: "در این پنل با انتخاب کشور و نوع کنشگر اطلاعاتی درمورد کنشگران در پایین نمایش داده می‌شود."
    }, {
        element: document.querySelector('#country'),
        intro: "مجموعه سند مورد نظر خود را از این قسمت انتخاب نمایید."
    }, {
        // element: document.querySelector('.multi-select-container'),
        element: document.querySelector('#CollectiveActorSelect'),
        intro: "موضوع مورد نظر خود را انتخاب نمایید."
    }, {
        element: document.querySelector('#document_search'),
        intro: "با فشردن کلید نمایش می‌توانیداطلاعات مربوط به کنشگران را مشاهده نمایید."
    },{
        element: document.querySelector('#search_result_tab'),
        intro: "در این تب می‌توانید اطلاعات مربوط به کنشگران، نشان داده می‌شود."
    }, {
        element: document.querySelector('#ExportExcel'),
        intro: "برای دانلوداطلاعات کنشگران در قالب اکسل، روی این گزینه کلیک نمایید."

    },{
        element: document.querySelector('#DownloadBtn'),
        intro: "برای دانلود اطلاعات کنشگران، روی این گزینه کلیک نمایید."

    }]
}).start();


}

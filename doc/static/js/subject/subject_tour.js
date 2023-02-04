function showTour(){
    introJs().setOptions({
    tooltipClass: 'customTooltip',
    nextLabel: 'بعدی',
    prevLabel: 'قبلی',
    doneLabel: 'اتمام',
    showProgress: false,
    steps: [{
        element: document.querySelector('#start'),
        intro: "در این پنل با انتخاب کشور و موضوع سند اسناد مرتبط با موضوع موردنظر ارائه و تحلیل اولیه می‌شود."
    }, {
        element: document.querySelector('#country'),
        intro: "مجموعه سند مورد نظر خود را از این قسمت انتخاب نمایید."
    }, {
        element: document.querySelector('.multi-select-container'),
        intro: "موضوع مورد نظر خود را انتخاب نمایید."
    }, {
        element: document.querySelector('#document_search'),
        intro: "با فشردن کلید نمایش می‌توانید اسناد مرتبط با موضوع انتخاب شده را مشاهده نمایید."
    },{
        element: document.querySelector('#result_doc'),
        intro: "در این تب می‌توانید لیست اسناد مرتبط با موضوع را به همراه کلیدواژه‌ها و امتیاز آن مشاهده نمایید."
    }, {
        element: document.querySelector('#without_subject'),
        intro: "در این تب می‌توانید اسنادی که مرتبط با هیچ‌یک از موضوعات موجود در لیست نیستند را مشاهده نمایید."
    }, {
        element: document.querySelector('#all_subject'),
        intro: "در این تب می‌توانید کلمات کلیدی مرتبط با موضوعات مختلف را مشاهده نمایید."
    }, {
        element: document.querySelector('#ExportExcel'),
        intro: "برای دانلود اسامی اسناد و اطلاعات جانبی آن‌ها در قالب اکسل، روی این گزینه کلیک نمایید."

    },{
        element: document.querySelector('#DownloadBtn'),
        intro: "برای دانلود متن اسناد ظاهر شده در نتیجه جستجو، روی این گزینه کلیک نمایید."

    }]
}).start();


}

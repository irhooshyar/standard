function showTour(){
    introJs().setOptions({
    tooltipClass: 'customTooltip',
    nextLabel: 'بعدی',
    prevLabel: 'قبلی',
    doneLabel: 'اتمام',
    showProgress: false,
    steps: [{
        element: document.querySelector('#start'),
        intro: "در این پنل می‌توانید با انتخاب مجموعه سند و یک کلیدواژه اصول حاوی آن کلیدواژه و اطلاعات مربوط به آن را مشاهده نمایید."
    }, {
        element: document.querySelector('#country'),
        intro: "مجموعه سند مورد نظر خود را از این قسمت انتخاب نمایید."
    }, {
        element: document.querySelector('#SearchBox'),
        intro: "کلیدواژه مورد نظر خود را وارد نمایید. با خالی گذاشتن این بخش تمامی اصول در تب‌های زیر نمایش داده می‌شوند. با انتخاب یک کلیدواژه، تنها اصولی نمایش داده می‌شوند که شامل آن کلیدواژه باشند."
    }, {
        element: document.querySelector('#document_search'),
        intro: "با کلیک بر روی این گزینه می‌توانید نتیجه جستجو را در تب های پایین مشاهده نمایید."
    },{
        element: document.querySelector('#keywords_info_tab'),
        intro: "در این تب می‌توانید اصول مندرج در مصوبات که حاوی کلیدواژه مورد نظر شماست را مشاهده نمایید."
    },{
        element: document.querySelector('#bar_chart_info_tab'),
        intro: "در این تب می‌توانید اطلاعات نموداری اصول را مشاهده نمایید."
    },{
        element: document.querySelector('#ExportExcel'),
        intro: "با کلیک روی این گزینه امکان دانلود اسامی و اطلاعات جانبی مربوط به اسناد حاصل از جستجو را خواهید داشت."

    },{
        element: document.querySelector('#DownloadBtn'),
        intro: "با کلیک روی این گزینه امکان دانلود اسناد حاصل از جستجو را خواهید داشت."

    }]
}).start();


}

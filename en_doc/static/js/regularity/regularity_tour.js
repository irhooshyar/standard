function showTour(){
    document.getElementById("advanced_fields").classList.add("show");
    introJs().setOptions({
    tooltipClass: 'customTooltip',
    nextLabel: 'بعدی',
    prevLabel: 'قبلی',
    doneLabel: 'اتمام',
    showProgress: false,
    steps: [{
        element: document.querySelector('#start'),
        intro: "در این پنل می‌توانید به تحلیل حوزه‌های مختلف تنظیم‌گری بپردازید. همچنین می‌توانید با وارد کردن کلیدواژه‌های کسب‌وکار موردنظر خود، اقدام به تحلیل تنظیم‌گران و ابزارهای تنظیم‌گری مرتبط با کسب‌وکار خود بپردازید."
    }, {
        element: document.querySelector('#country'),
        intro: "مجموعه سند مورد نظر خود را از این قسمت انتخاب نمایید."
    },  {
        element: document.querySelector('#advanced_search'),
        intro: "با کلیک روی این گزینه، تنظیمات پیشرفته  مرتبط با  تنظیم‌گری نمایش داده می‌شود."
    }, {
        element: document.querySelector('#document_search'),
        intro: "با کلیک روی این گزینه نتایج متناظر با ورودی‌های تعیین‌شده ارائه خواهند شد."
    },{
        element: document.querySelector('#KeywordsBox'),
        intro: "کلیدواژگان متناظر با کسب‌وکار مدنظر را در این قسمت  وارد نمایید. از «/» به عنوان جداکننده کلیدواژگان بهره بجویید. به عنوان نمونه با جستجوی کلیدواژه‌های «سازمان/مجوز» اطلاعات مربوط به اسنادی نمایش داده می‌شوند که شامل سازمان یا مجوز و یا هردو آن‌ها هستند."
    },{
        element: document.querySelector('#RegularityAreaSelect'),
        intro: "از این قسمت حوزه تنظیم‌گری مورد نظر خود را  انتخاب نمایید."
    },{
        element: document.querySelector('#RegulatorSelect'),
        intro: "از این قسمت  تنظیم‌گر مورد نظر خود را  انتخاب نمایید."
    },{
        element: document.querySelector('.multi-select-container'),
        intro: "از این قسمت ابزار(های) تنظیم‌گری مورد نظر خود را  انتخاب نمایید."
    },{
        element: document.querySelector('#search_result_tab'),
        intro: "با توجه به موارد تعیین شده در  تنظیمات پیشرفته  (کلیدواژگان کسب‌وکار، حوزه تنظیم‌گری و موارد دیگر)، در این تب اسناد مرتبط با گزینه‌ها لیست می‌شوند. کاربر امکان مرتب سازی نتایج بر اساس یک ستون خاص را دارا می‌باشد."
    },{
        element: document.querySelector('#regulators_graph_tab'),
        intro: "در این تب گراف تنظیم‌گران براساس گزینه‌های تعیین شده نمایش داده می‌شود."
    },{
        element: document.querySelector('#information_chart_tab'),
        intro: "در این تب اطلاعات نموداری مرتبط با ابزارهای تنظیم‌گری در قالب نمودارهای ستونی و دایره‌ای نمایش داده می‌شود."
    },{
        element: document.querySelector('#ExportExcel'),
        intro: "با کلیک روی این گزینه امکان دانلود اسامی و اطلاعات جانبی مربوط به اسناد حاصل از جستجو را خواهید داشت."
    },{
        element: document.querySelector('#DownloadBtn'),
        intro: "با کلیک روی این گزینه امکان دانلود اسناد حاصل از جستجو را خواهید داشت."
    }]
}).start();


}

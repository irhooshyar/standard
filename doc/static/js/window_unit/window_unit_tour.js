function showTour(){
    introJs().setOptions({
    tooltipClass: 'customTooltip',
    nextLabel: 'بعدی',
    prevLabel: 'قبلی',
    doneLabel: 'اتمام',
    showProgress: false,
    steps: [{
        element: document.querySelector('#start'),
        intro: "در این پنل می‌توانید به بررسی اسناد حاوی پنجره واحد بپردازید."
    }, {
        element: document.querySelector('#country'),
        intro: "مجموعه سند مورد نظر خود را از این قسمت انتخاب نمایید."
    }, {
        element: document.querySelector('#document_search'),
        intro: "با کلیک روی این گزینه اسناد متناظر با پنجره واحد در کشور انتخاب شده ارائه خواهند شد."
    },{
        element: document.querySelector('#search_result_tab'),
        intro: "در این تب اسناد مرتبط با پنجره واحد لیست می‌شوند. کاربر امکان مرتب سازی نتایج بر اساس یک ستون خاص را دارا می‌باشد. همچنین جزئیات مربوط به هر سند و تحلیل‌های متناظر با هر پاراگراف نیز موجود است."
    },{
        element: document.querySelector('#window_unit_chart_tab'),
        intro: "در این تب، اطلاعات مربوط به کلمات پس از پنجره واحد نمایش داده شده‌است. با کلیک روی نمودارها می‌توانید اطلاعات بیش‌تری را مشاهده نمایید."
    },{
        element: document.querySelector('#ExportExcel'),
        intro: "با کلیک روی این گزینه امکان دانلود اسامی و اطلاعات جانبی مربوط به اسناد حاصل از جستجو را خواهید داشت."
    },{
        element: document.querySelector('#DownloadBtn'),
        intro: "با کلیک روی این گزینه امکان دانلود اسناد حاصل از جستجو را خواهید داشت."
    }]
}).start();


}

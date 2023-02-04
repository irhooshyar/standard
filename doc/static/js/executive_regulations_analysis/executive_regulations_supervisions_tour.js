function showTour(){
    introJs().setOptions({
    tooltipClass: 'customTooltip',
    nextLabel: 'بعدی',
    prevLabel: 'قبلی',
    doneLabel: 'اتمام',
    showProgress: false,
    steps: [{
        element: document.querySelector('#start'),
        intro: "در این پنل می‌توانید آئین‌نامه‌های اجرایی و مراجع ناظر بر آن ها را مشاهده کنید."
    }, {
        element: document.querySelector('#country'),
        intro: "مجموعه سند مورد نظر خود را از این قسمت انتخاب نمایید."
    }, {
        element: document.querySelector('#document_search'),
        intro: "با کلیک روی این گزینه آئین‌نامه‌های اجرایی در کشور انتخاب شده ارائه خواهند شد."
    },{
        element: document.querySelector('#search_result_tab'),
        intro: "در این تب آئین‌نامه‌های اجرایی و مراجع ناظر بر آن ها لیست می‌شوند. همچنین در جزئیات مربوط به هر آئین‌نامه‌ اجرایی می توانید نوشتپار مربوطه را مشاهده کنید."
    },{
        element: document.querySelector('#bar_chart_info_tab'),
        intro: "در این تب نتایج حاصل در قالب نمودار نمایش داده می شوند."
    },{
        element: document.querySelector('#ExportExcel'),
        intro: "با کلیک روی این گزینه امکان دانلود اسامی آیین نامه ها، اطلاعات آیین نامه ها و مراجع ناظر بر آن ها در قالب یک فایل اکسل را دارید."
    },{
        element: document.querySelector('#DownloadBtn'),
        intro: "با کلیک روی این گزینه امکان دانلود اسناد حاصل از جستجو را خواهید داشت."
    }]
}).start();


}

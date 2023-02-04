function showTour(){
    introJs().setOptions({
    tooltipClass: 'customTooltip',
    nextLabel: 'بعدی',
    prevLabel: 'قبلی',
    doneLabel: 'اتمام',
    showProgress: false,
    steps: [{
        element: document.querySelector('#start'),
        intro: "در این پنل می‌توانید به بررسی آئین‌نامه‌های اجرایی و قانون متناظر آن ها بپردازید."
    }, {
        element: document.querySelector('#country'),
        intro: "مجموعه سند مورد نظر خود را از این قسمت انتخاب نمایید."
    }, {
        element: document.querySelector('#document_search'),
        intro: "با کلیک روی این گزینه اسناد مربوط به آئین‌نامه‌های اجرایی در کشور انتخاب شده ارائه خواهند شد."
    },{
        element: document.querySelector('#search_result_tab'),
        intro: "در این تب اسناد مرتبط باآئین‌نامه‌های اجرایی لیست می‌شوند. همچنین جزئیات مربوط به هر آئین‌نامه‌ اجرایی و قانون متناظر با آن نیز موجود است."
    },{
        element: document.querySelector('#unknown_result_tab'),
        intro: "در این تب اسناد مرتبط باآئین‌نامه‌های اجرایی که قانون متناظرشان پیدا نشده است، لیست می‌شوند."
    },{
        element: document.querySelector('#probable_regulators_tab'),
        intro: "در این تب، پاراگراف هایی که آیین نامه هستند با بررسی کنشگرهایشان، به عنوان آیین نامه محتمل لیست شده اند."
    },{
        element: document.querySelector('#ExportExcel'),
        intro: "با کلیک روی این گزینه امکان دانلود اسامی آیین نامه ها و قوانین آن ها به همراه شماره بند قانونی در قالب یک فایل اکسل را دارید."
    },{
        element: document.querySelector('#DownloadBtn'),
        intro: "با کلیک روی این گزینه امکان دانلود اسناد حاصل از جستجو را خواهید داشت."
    }]
}).start();


}

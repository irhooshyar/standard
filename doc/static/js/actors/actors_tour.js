function showTour() {
  introJs()
    .setOptions({
      tooltipClass: "customTooltip",
      nextLabel: "بعدی",
      prevLabel: "قبلی",
      doneLabel: "اتمام",
      showProgress: false,
      steps: [
        {
          element: document.querySelector("#start"),
          intro:
            "در این پنل می‌توانید، با انتخاب لیستی از کلیدواژه‌ها، نوع کنشگر و نقش آن اطلاعات مهمی از اسناد و کنشگران حاوی لیست موردنظر بدست آورید.",
        },
        {
          element: document.querySelector("#country"),
          intro: "مجموعه سند مورد نظر خود را از این قسمت انتخاب نمایید.",
        },
        {
          element: document.querySelector('#advanced_search'),
          intro: "با کلیک بر روی این گزینه، تنظیمات پیشرفته فعال می‌شود."
        },
        {
          element: document.querySelector('#document_search'),
          intro: "با کلیک بر روی این گزینه، اطلاعات مورد نظر در تب های پایین نمایش داده می‌شود."
        },
        {
          element: document.querySelector('#KeywordsBox'),
          intro: "لیستی از کلیدواژه‌های مورد نظر خود را وارد نمایید. به عنوان نمونه: «سازمان/مجوز»"
        },
          {
            element: document.querySelector('#ActorCategorySelect'),
            intro:"با کلیک بر روی این گزینه، نوع کنشگر موردنظر را انتخاب نمایید."
          },
        {
          element: document.querySelector('.ActorSelect .multi-select-container'),
          intro: "با کلیک بر روی این گزینه، کنشگر مورد نظر خود را انتخاب نمایید.",
        },{

          element: document.querySelector('.ActorRoleSelect .multi-select-container'),
          intro: "با کلیک بر روی این گزینه، نقش کنشگر مورد نظر خود را انتخاب نمایید."

        },{

          element: document.querySelector('#actor_result_tab'),
          intro: "در این تب اطلاعاتی در مورد کنشگران و نقش آن‌ها با جزییات بر روی جدول قابل مشاهده است."

        },{

          element: document.querySelector('#search_result_tab'),
          intro: "در این تب می‌توانید اطلاعاتی درمورد اسناد مرتبط با کلیدواژه و کنشگر انتخابی بدست آورید."

        },{

          element: document.querySelector('#chart_info_tab'),
          intro: ".در این تب می‌توانید اطلاعات مربوط به هر کنشگر را بر حسب تعداد پاراگراف حاوی آن کنشگر مشاهده نمایید."

        },{

          element: document.querySelector('#actors_graph_tab'),
          intro: "در این تب می‌توانید گراف کلیدواژه و کنشگر را مشاهده نمایید."

        },{

          element: document.querySelector('#actors_supervisors_tab'),
          intro: "در این تب می‌توانید گراف نظارت را مشاهده نمایید."

        },
          {
        element: document.querySelector('#ExportExcel'),
        intro: "با کلیک روی این گزینه امکان دانلود اسامی و اطلاعات جانبی مربوط به اسناد حاصل از جستجو را خواهید داشت."

        },
          {
        element: document.querySelector('#DownloadBtn'),
        intro: "با کلیک روی این گزینه امکان دانلود اسناد حاصل از جستجو را خواهید داشت."

    }
      ],
    })
    .start();
}

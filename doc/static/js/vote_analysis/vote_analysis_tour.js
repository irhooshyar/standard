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
            "در این پنل می‌توانید با انتخاب کشور و یک یا چند رأی، اطلاعات آماری، اطلاعات مربوط به کلیدواژگان و توزیع کلید واژگان در آن رأی را بررسی نمایید.",
        },
        {
          element: document.querySelector("#country"),
          intro: "مجموعه سند مورد نظر خود را از این قسمت انتخاب نمایید.",
        },
        {
          element: document.querySelector("#document_select"),
          intro:
            "با انتخاب یک یا چند رأی می‌توانید اطلاعات مربوط به آن را در تب‌های پایین مشاهده نمایید.",
        },
        {
          element: document.querySelector("#keywords_info_tab"),
          intro:
            "در این تب، تعداد تکرار هر کلیدواژه به تفکیک هر رأی نشان داده شده است.",
        },
        {
          element: document.querySelector("#statistics_info_tab"),
          intro:
            "در این تب، اطلاعاتی در مورد موضوع آراء انتخاب شده، سال صدور رأی و مرجع صدور رأی ارائه می‌شود.",
        },
        {
          element: document.querySelector("#keywords_distribution_tab"),
          intro:
            "در این تب، توزیع کلیدواژگان آرای انتخابی، بر روی نمودار هیستوگرام نشان داده شده است. ",
        },
        {
          element: document.querySelector("#ExportExcel"),
          intro:
            "برای دانلود اسامی آراء و اطلاعات جانبی آن‌ها در قالب اکسل، روی این گزینه کلیک نمایید.",
        },
        {
          element: document.querySelector("#DownloadBtn"),
          intro:
            "برای دانلود متن آراء ظاهر شده در نتیجه جستجو، روی این گزینه کلیک نمایید.",
        },
      ],
    })
    .start();
}

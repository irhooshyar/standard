let person_rows = []
init()

function init() {
    const menu_columns = {
        "v_positive_sentiment": 'احساس بسیار مثبت',
        "positive_sentiment": 'احساس مثبت',
        "mixed_sentiment": 'احساس خنثی',
        "v_negative_sentiment": 'احساس بسیار منفی',
        "negative_sentiment": 'احساس منفی',
        "no_sentiment": 'بدون ابراز احساسات',
    }
    append_column(menu_columns, "PersonColumnSelect")
}

async function get_real_persons(generated_persons) {
    person_rows = generateRows(generated_persons)

    const paragraph_table_tab = document.getElementById("paragraph_person_info_tab")
    if (paragraph_table_tab.classList.contains("active")) {
        document.getElementById("SearchResultLable").innerText = "تعداد کل نتایج: " + generated_persons.length + " فرد"
    }
    paragraph_table_tab.addEventListener("click", () => {
        document.getElementById("SearchResultLable").innerText = "تعداد کل نتایج: " + generated_persons.length + " فرد"
    })

    startBlockUI('paragraph_info_pane');
    table_show_result();

}

function generateRows(persons) {
    const rows = []

    let counter = 1
    for (const person of persons) {
        const v_positive_count = person['value']['احساس بسیار مثبت'] ? person['value']['احساس بسیار مثبت']['doc_count'] : 0
        const positive_count = person['value']['احساس مثبت'] ? person['value']['احساس مثبت']['doc_count'] : 0
        const mixed_sentiment_count = person['value']['احساس خنثی یا ترکیبی از مثبت و منفی'] ? person['value']['احساس خنثی یا ترکیبی از مثبت و منفی']['doc_count'] : 0
        const negative_sentiment_count = person['value']['احساس منفی'] ? person['value']['احساس منفی']['doc_count'] : 0
        const v_negative_sentiment_count = person['value']['احساس بسیار منفی'] ? person['value']['احساس بسیار منفی']['doc_count'] : 0
        const no_sentiment_count = person['value']['بدون ابراز احساسات'] ? person['value']['بدون ابراز احساسات']['doc_count'] : 0

        const modal_function = `show_person_modal('${person['key']}')`
        const detail = '<button type="button" class="btn modal_btn" data-bs-toggle="modal" onclick="' + modal_function + '" data-bs-target="#ChartModal_2">جزئیات</button>'


        const row = {}
        row['id'] = counter
        row['person_name'] = person['key']
        row['all_repetition'] = v_negative_sentiment_count + no_sentiment_count + negative_sentiment_count
            + mixed_sentiment_count + positive_count + v_positive_count;
        row['v_positive_sentiment'] = v_positive_count
        row['positive_sentiment'] = positive_count
        row['mixed_sentiment'] = mixed_sentiment_count
        row['v_negative_sentiment'] = v_negative_sentiment_count
        row['no_sentiment'] = no_sentiment_count
        row['negative_sentiment'] = negative_sentiment_count
        row['detail'] = detail

        rows.push(row)
        counter++;
    }

    return rows
}

async function show_person_modal(personKey) {
    const field_name = CHART_FIELD_DICT['person_container'] + '.keyword'
    const chart_name = CHART_NAME_DICT['person_container']

    GetClickedColumnParagraphs(chart_name, field_name, personKey.replaceAll("#", "*"), false, true)
}


async function tableExportExcel() {
    let csv = FooTable.get('#PersonsTable').toCSV();
    const btn_regex = new RegExp('<button.*</button>', 'g')
    csv = csv.replaceAll("#", "")
    csv = csv.replaceAll(btn_regex, "")

    let save_file_name = "افراد حقیقی {" + document.getElementById("SearchBox").value + "}"

    let csvContent = "data:text/csv;charset=utf-8,%EF%BB%BF" + encodeURI(csv);
    const link = document.createElement("a");
    link.setAttribute("href", csvContent);
    link.setAttribute("download", save_file_name + ".csv");
    document.body.appendChild(link);
    link.click()
}

function table_show_result() {


    let selected_columns = ["id", "person_name", "all_repetition", "detail"]
    selected_columns = find_selected_column(selected_columns, "PersonColumnSelect")

    const PersonTableColumns = [
        {
            "name": "id",
            "title": "ردیف",
            "breakpoints": "xs sm",
            "type": "number",
            "style": {
                "width": "5%"
            }
        },
        {
            "name": "person_name",
            "title": "نام فرد",
        },
        {
            "name": "all_repetition",
            "title": "تعداد احکام حاوی نام",
            "type": "number",
            "style": {
                "width": "8%"
            }
        },
        {
            "name": "v_positive_sentiment",
            "title": "تعداد احساس بسیار مثبت",
            "type": "number",
            "style": {
                "width": "8%"
            }
        },
        {
            "name": "positive_sentiment",
            "title": "تعداد احساس مثبت",
            "type": "number",
            "style": {
                "width": "8%"
            }
        },
        {
            "name": "mixed_sentiment",
            "title": "تعداد احساس خنثی",
            "type": "number",
            "style": {
                "width": "8%"
            }
        },
        {
            "name": "v_negative_sentiment",
            "title": "تعداد احساس بسیار منفی",
            "type": "number",
            "style": {
                "width": "8%"
            }
        },
        {
            "name": "negative_sentiment",
            "title": "تعداد احساس منفی",
            "type": "number",
            "style": {
                "width": "8%"
            }
        },
        {
            "name": "no_sentiment",
            "title": "تعداد بدون ابراز احساسات",
            "type": "number",
            "style": {
                "width": "8%"
            }
        },
        {
            "name": "detail",
            "title": "جزئیات",
            "style": {
                "width": "8%"
            }
        },
    ]

    if (!selected_columns.includes("all")) {
        for (let column of PersonTableColumns) {
            if (selected_columns.includes(column["name"])) {
                column["visible"] = true
            } else {
                column["visible"] = false
            }
        }
    }


    $('#PersonsTable').empty();
    $('#PersonsTable').footable({
        "paging": {
            "enabled": true,
            strings: {
                first: '»',
                prev: '›',
                next: '‹',
                last: '«'
            }
        },
        "filtering": {
            "enabled": true,
            "placeholder": "نام فرد...."
        },
        "sorting": {
            "enabled": true
        },
        "empty": "فردی یافت نشد.",

        "columns": PersonTableColumns,
        "rows": person_rows
    })
}
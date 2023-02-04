let rule_rows = []
init()

function init() {
    const menu_columns = {
        "rahbari_type": 'نوع سند',
        "rahbari_date": 'تاریخ',
        "rahbari_labels": 'برچسب'
    }
    append_column(menu_columns, "RuleColumnSelect")
}

async function get_rahbari_rule(country_id, type_id, label_name, from_year, to_year, place, text, search_type, curr_page) {
    document.getElementById('RuleTablePaginationInput').disabled = true;
    const rahbari_type = 0
    const request_link = 'http://' + location.host + "/SearchRahbariRule_ES/" + country_id + "/" + type_id + "/" +
        label_name + "/" + from_year + "/" + to_year + "/" + rahbari_type + "/" + place + "/" + text + "/" + search_type + "/"
        + curr_page + "/";

    startBlockUI('paragraph_rule_info_pane');
    let response = await fetch(request_link).then(response => response.json());

    const total_hits = response["total_hits"]
    const result = response["result"]

    const paragraph_tab = document.getElementById("paragraph_rule_info_tab")
    if (paragraph_tab.classList.contains("active")) {
        document.getElementById("SearchResultLable").innerText = "تعداد کل نتایج: " + total_hits + " سند"
    }
    paragraph_tab.addEventListener("click", () => {
        document.getElementById("SearchResultLable").innerText = "تعداد کل نتایج: " + total_hits + " سند"
    })

    update_table_pagination_input(curr_page, total_hits, "RuleTablePaginationInput", "rule_from_page", "rule_total_page")

    console.log(result)
    rule_rows = generate_rahbari_rule_rows(result, search_type, text)

    show_rule_table_results()

    document.getElementById('RuleTablePaginationInput').disabled = false;
    stopBlockUI('paragraph_rule_info_pane');
}

function generate_rahbari_rule_rows(results, search_type, text) {
    let rows = []

    let counter = 1
    for (let doc of results) {
        const doc_id = doc['_source']['document_id']
        const doc_name = doc['_source']['name']
        const doc_file_name = doc['_source']['document_file_name']
        const type = doc['_source']['type']
        const rahbari_date = doc['_source']['rahbari_date']
        const rahbari_year = doc['_source']['rahbari_year'] !== 0 ? doc['_source']['rahbari_year'] : 'نامشخص'
        const labels = doc['_source']['labels']

        let is_disabled = ""
        if (text === "empty")
            is_disabled = "disabled"

        const detail_function = `DetailFunction2('${doc_id}','${doc_name}','${search_type}','${text}', ${1})`;
        const detail = '<button type="button" class="btn modal_btn" data-bs-toggle="modal" ' + ' onclick="' + detail_function + '" data-bs-target="#myModal" ' + is_disabled + '>جزئیات</button>'

        const document_link = 'http://' + location.host + "/information/?id=" + doc_id
        const doc_name_link = '<a target="blank" href="' + document_link + '">' + doc_name + "</a>"

        const row = {
            "index": counter,
            "doc_id": doc_id,
            "doc_name": doc_name_link,
            "doc_file_name": doc_file_name,
            "rahbari_date": rahbari_date,
            "rahbari_year": rahbari_year,
            "rahbari_type": type,
            "rahbari_labels": labels,
            "detail": detail
        }

        rows.push(row)
        counter++;
    }
    return rows
}

// function detail_rahbari_function(doc_ic, search_type, text) {
//     const request_link = 'http://' + location.host + "/GetSearchDetails_ES_Rahbari_2/" + doc_ic + "/" + search_type + "/" + text + "/" + 1 + "/";
//     GetClickedColumnParagraphs("احکام دارای", " ", "باید و نباید", false, false, request_link)
// }

function show_rule_table_results() {
    let selected_columns = ["index", "doc_name", "detail"]
    selected_columns = find_selected_column(selected_columns, "RuleColumnSelect")

    const RuleTableColumns = [{
        "name": "index",
        "title": "ردیف",
        "breakpoints": "xs sm",
        "type": "number",
        "style": {
            "width": "5%"
        }
    }, {
        "name": "doc_name",
        "title": "نام سند",
        "style": {
            "width": "35%"
        }
    }, {
        "name": "rahbari_type",
        "title": "نوع سند",
        "style": {
            "width": "10%"
        }
    }, {
        "name": "rahbari_date",
        "title": "تاریخ",
        "style": {
            "width": "10%"
        }
    }, {
        "name": "rahbari_labels",
        "title": "برچسب",
        "style": {
            "width": "25%"
        }
    }, {
        "name": "detail",
        "title": "جزئیات",
        "style": {
            "width": "5%"
        }
    }]

    if (!selected_columns.includes("all")) {
        for (let column of RuleTableColumns) {
            if (selected_columns.includes(column["name"])) {
                column["visible"] = true
            } else {
                column["visible"] = false
            }
        }
    }


    $('#RuleSearchTable').empty();
    $('#RuleSearchTable').footable({
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
            "enabled": false,
        },
        "sorting": {
            "enabled": true
        },
        "empty": "سندی یافت نشد.",

        "columns": RuleTableColumns,
        "rows": rule_rows
    })
}
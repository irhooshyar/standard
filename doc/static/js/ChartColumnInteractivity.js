class ColumnInteractivity {
    current_page_number = 1;
    min_page_number = 1;
    max_page_number = 1;

    check_box_status = {}
    segmentation_agg = {}
    total_hits = 0

    constructor(
        content_type,
        request_configs,
        export_configs,
        modal_configs,
        highlight_configs,
        segmentation_config
    ) {
        this.content_type = content_type; // documents, paragraphs, custom

        this.request_link = request_configs["link"]; // link must be without cur_page & search result_size
        this.search_result_size = request_configs["search_result_size"];
        this.data_type = request_configs["data_type"];
        this.form_data = request_configs["form_data"];
        this.max_result_window = request_configs["max_result_window"];

        this.modal_body_id = modal_configs["body_id"];
        this.modal_load_more_btn_id = modal_configs["modal_load_more_btn_id"];
        this.modal_result_size_container_id =
            modal_configs["result_size_container_id"];
        this.result_size_message = modal_configs["result_size_message"];

        this.modal_list_type = modal_configs["list_type"];
        this.custom_body_function = modal_configs["custom_body_function"];
        this.custom_body_parameters = modal_configs["body_parameters"];

        this.segmentation_parameters = segmentation_config['parameters']
        this.segmentation_keyword = segmentation_config['keyword']
        this.segmentation_aggregation_keyword = segmentation_config['aggregation_keyword']
        this.segmentation_enabled = segmentation_config['enable']

        this.custom_highlight_function = highlight_configs["custom_function"];
        (this.highlight_parameters = highlight_configs["parameters"]),
            (this.highlight_enabled = highlight_configs["highlight_enabled"]);

        this.export_link = export_configs["link"]; // link must be without cur_page & search result_size
        this.export_btn_id = export_configs["btn_id"];
    }

    async download_content() {
        const new_link =
            this.export_link +
            this.current_page_number +
            "/" +
            this.search_result_size +
            "/";

        const response = await fetch(new_link).then((response) => response.json());
        const file_name = response["file_name"];
        const path = "http://" + location.host + "/media/" + file_name;
        const link = document.createElement("a");
        link.href = path;
        link.click();
    }

    async load_content() {
        const _this = this

        const new_link =
            this.request_link +
            this.current_page_number +
            "/" +
            this.search_result_size +
            "/";

        let response = "";

        if (this.data_type == "form_data") {

            function ajaxAwait() {
                return $.ajax({
                    url: new_link,
                    data: _this.form_data,
                    type: "POST",
                    contentType: false,
                    processData: false,
                    async: true,
                })
                    .done(function (res) {
                        response = res;
                        const result_content = response["result"];
                        const total_hits = response["total_hits"];

                        document.getElementById(_this.modal_result_size_container_id).innerHTML = "<p>" +
                            total_hits + " " + _this.result_size_message + ":"
                            + "</p>";

                        _this.update_max_page_number(total_hits);
                        _this.show_modal_body(result_content);
                    })
                    .fail(function (res) {
                        console.log("fail");
                    });
            }

            await ajaxAwait()

        } else {
            response = await fetch(new_link).then((response) => response.json());
            const result_content = response["result"];
            const total_hit = response["total_hits"];

            document.getElementById(this.modal_result_size_container_id).innerHTML = "<p>" +
                total_hit + " " + this.result_size_message + ":" + "</p>";

            if (this.segmentation_enabled) {
                const aggregations = response['aggregations'][this.segmentation_aggregation_keyword]['buckets']
                for (const agg of aggregations) {
                    this.segmentation_agg[agg['key']] = agg['doc_count']
                }
            }

            this.update_max_page_number(total_hit);
            this.show_modal_body(result_content);
        }

        return response
    }

    update_max_page_number(total_hits) {
        this.total_hits = total_hits;
        let page_count = 0;

        if (total_hits < this.search_result_size) {
            page_count = 1;
        } else if (total_hits < this.max_result_window) {
            page_count = Math.ceil(total_hits / this.search_result_size);
        } else if (total_hits >= this.max_result_window) {
            page_count = this.max_result_window / this.search_result_size;
        }

        this.max_page_number = page_count;
    }

    show_modal_body(result_content) {
        const curr_page = this.current_page_number;
        const max_page = this.max_page_number;

        if (this.segmentation_enabled) {
            this.create_segmentation_box();
        }

        let modal_content = this.create_modal_body(result_content);

        const index = (curr_page - 1) * this.search_result_size + 1;

        if (index === 1) {
            if (this.modal_list_type === "ordered") {
                modal_content = "<ol start='" + index + "'>" + modal_content + "</ol>";
            } else {
                modal_content = "<ul>" + modal_content + "</ul>";
            }
            document.getElementById(this.modal_body_id).innerHTML += modal_content;
        }else{
            document.getElementById(this.modal_body_id).firstElementChild.innerHTML += modal_content;
        }


        if (curr_page >= max_page) {
            $("#" + this.modal_load_more_btn_id).hide();
        } else {
            $("#" + this.modal_load_more_btn_id).show();
        }

        /* LoadMoreDocuments */
        const _this = this;
        document.getElementById(this.modal_load_more_btn_id).onclick = function () {
            // startFullPageBlockUI();

            if (_this.current_page_number < _this.max_page_number) {
                _this.current_page_number = _this.current_page_number + 1;
            }

            _this.load_content();
            // stopFullPageBlockUI('نمایش بیش‌تر');
        };
    }

    create_modal_body(result_content) {
        let body_content = "";

        if (this.content_type == "paragraphs") {
            body_content = this.create_paragraphs_body(result_content);
        } else if (this.content_type == "documents") {
            body_content = this.create_documents_body(result_content);
        } else if (this.content_type == "custom") {
            body_content = this.create_custom_body(result_content);
        }

        return body_content;
    }

    create_documents_body(result_documents) {
        let body_content = "";

        for (const doc of result_documents) {

            const link =
                "http://" +
                location.host +
                "/information/?id=" +
                doc["_source"]["document_id"];
            let tag =
                "<li class='mt-3' id=" +
                doc["_source"]["document_id"] +
                "><a target='blank' href='" +
                link +
                "'>" +
                doc["_source"]["name"] +
                "</a></li>";
            body_content += tag;
        }

        return body_content;
    }

    create_paragraphs_body(result_paragraphs) {
        let body_content = "";
        let paragraph_keyword = ""
        let text = ''
        let document_name = "";

        for (let para of result_paragraphs) {
            const document_id = para["_source"]["document_id"];
            const paragraph_id = para["_source"]["paragraph_id"];
            let tag_display = "list-item";


            if ("document_name" in para["_source"]) {
                document_name = para["_source"]["document_name"];
            } else {
                document_name = para["_source"]["name"];
            }


            try {
                text = para["highlight"]["attachment.content"][0]
            } catch (error) {
                text = para["_source"]["attachment"]["content"]
            }

            const doc_link =
                "http://" + location.host + "/information/?id=" + document_id;
            let doc_tag =
                "<a title='پروفایل سند' class='bold text-secondary' target='blank' href='" +
                doc_link +
                "'>" +
                document_name +
                "</a>";

            if (this.highlight_enabled) {
                text = this.highlight_function(text);
            }

            const paragraph_link =
                "http://" + location.host + "/sentiment_analysis/?id=" + paragraph_id;

            const paragraph_tag =
                "<a class='' title = 'پروفایل حکم' target='blank' href='" +
                paragraph_link +
                "'>" +
                text +
                "</a>";

            if (this.segmentation_enabled) {

                if (this.segmentation_keyword in para["_source"]) {
                    paragraph_keyword = para["_source"][this.segmentation_keyword]

                    doc_tag += "<a class='bold text-secondary'>" + paragraph_keyword + "</a>"

                    if (this.check_box_status[paragraph_keyword] === false) {
                        tag_display = "none"
                        this.set_total_hit()
                    }
                }
            }

            const tag = `<li class='mb-3 lh-lg' data-model-name='${paragraph_keyword}' style="display: ${tag_display}">` + doc_tag + paragraph_tag + "</li>";
            body_content += tag;
        }

        return body_content;
    }

    create_custom_body(result_content) {
        let body_content = this.custom_body_function(
            result_content,
            this.custom_body_parameters
        );
        return body_content;
    }

    highlight_function(paragraph) {
        paragraph = this.custom_highlight_function(
            paragraph,
            this.highlight_parameters
        );
        return paragraph;
    }

    create_segmentation_box() {
        const header = document.getElementById(this.modal_result_size_container_id)
        const check_box_container = document.createElement('div');

        check_box_container.style.marginBlock = 15 + "px";
        header.style.display = "grid"

        for (let i = 0; i < this.segmentation_parameters.length; i++) {
            let check_box_checked = "checked"
            const parameter = this.segmentation_parameters[i];
            let child = ''

            if (this.check_box_status[parameter] !== false && this.check_box_status[parameter] !== true) {
                this.check_box_status[parameter] = true
            } else if (this.check_box_status[parameter] === false) {
                check_box_checked = ""
            }

            child = '<div class="form-check form-check-inline float-right py-2 pb-1">' +
                '<input data-model-name="check-box-input" class="form-check-input topic_keyword' + '" id="kw_' + i + '" style="padding:0;"  type="checkbox" value="' + parameter + '" ' + check_box_checked + '>' +
                '<label class="form-check-label">' + parameter + '</label> ' +
                '</div>'

            check_box_container.innerHTML += child
        }
        header.insertBefore(check_box_container, header.firstChild)


        const check_boxes = document.querySelectorAll("[data-model-name='check-box-input']")
        for (const check_box of check_boxes) {
            check_box.addEventListener('change', (event) => {
                const element = event.target
                const value = element.getAttribute('value')
                const targets = document.querySelectorAll(`[data-model-name='${value}']`)
                const modal_body = document.getElementById(this.modal_body_id)

                if (element.checked) {
                    for (const hokm of targets) {
                        hokm.style.display = "list-item"
                        this.check_box_status[value] = true
                    }
                } else {
                    for (const hokm of targets) {
                        hokm.style.display = "none"
                        this.check_box_status[value] = false
                    }
                }
                this.set_total_hit()
            })
        }
    }

    set_total_hit() {
        let number = this.total_hits;
        for (const key of this.segmentation_parameters) {
            if (this.check_box_status[key] === false) {
                number = number - (this.segmentation_agg[key] ? this.segmentation_agg[key] : 0);
            }
        }
        const pTag = document.getElementById(this.modal_result_size_container_id).lastElementChild
        pTag.innerHTML = number + " " + this.result_size_message + ":"
    }
}

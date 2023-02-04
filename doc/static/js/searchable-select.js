
function initSearchableSelects() {
    document.querySelectorAll('.searchable-select').forEach((el) => {
        new TomSelect(el, {
            create: false,
            maxItems: 1,
            maxOptions: null,
            render: {
                no_results: function () {
                    return '<div class="no-results">نتیجه‌ای یافت نشد.</div>';
                },
            },
            //default value
            onBlur: function () {
                if (!this.getValue()) {
                    this.setValue(Object.values(this.options)[0].value);
                    this.setCaret(0)
                }
            }
        });
    });

    document.querySelectorAll('.searchable-multi-select').forEach((el) => {
        new TomSelect(el, {
            plugins: {
                remove_button:{
                    title:'حذف',
                    className: 'remove-searchable-item'
                }
            },
            create: false,
            maxItems: null,
            maxOptions: null,
            render: {
                no_results: function () {
                    return '<div class="no-results">نتیجه‌ای یافت نشد.</div>';
                },
            },
            //default value
            onBlur: function () {
                if (this.getValue().length==0) {
                    this.setValue([Object.values(this.options)[0].value]);
                    this.setCaret(0)
                }
            },
            onItemRemove: function () {
                if (this.getValue().length==0) {
                    this.setValue([Object.values(this.options)[0].value]);
                    this.setCaret(0)
                }
            },
            onItemAdd: function (value, $item) {
                if (value==="all" || value==="0"){
                    return
                }

                this.removeItem("all", true)
                this.removeItem("0", true)
                

            }
        });
    });
}

function syncSelect(id, noReset) {
    let select = document.getElementById(id);
    let control = select.tomselect;
    control.sync();
    if (!noReset) {
        resetSelectValue(control);
    }
}

function syncSelectOptions(id, options, noReset) {
    let select = document.getElementById(id);
    let control = select.tomselect;
    control.clear();
    control.clearOptions(() => false);
    control.addOptions(options);
    if (!noReset)
        resetSelectValue(control);
}

function syncAllSelects(noReset) {
    document.querySelectorAll('select.searchable-select').forEach((el) => {
        let control = el.tomselect;
        control.sync();
        if (!noReset)
            resetSelectValue(control);
    });
}

function syncAllSelectsWithResetExceptions(exceptions, noReset) {
    document.querySelectorAll('select.searchable-select').forEach((el) => {
        let control = el.tomselect;
        control.sync();
        if (exceptions.some(e => el.id === e)) {
            return;
        }
        if (!noReset)
            resetSelectValue(control);
    });
}

function resetSelectValue(control) {
        const option = Object.values(control.options)[0] || {};
        control.setValue(option.value);
        control.setCaret(0)
}

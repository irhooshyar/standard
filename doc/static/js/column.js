function append_column(columns, id="ColumnSelect") {
    let options = [{ value: "all", text: "همه"}];

    for (column in columns) {
        options.push( { value: column, text: columns[column] });
    }

    syncSelectOptions(id, options)
}

function find_selected_column(selected_columns, id="ColumnSelect") {
    var e = document.getElementById(id);
    var selected = [...e.options]
        .filter(option => option.selected)
        .map(option => option.value)

    for (let i = 0; i < selected.length; i++) {
        selected_columns.push(selected[i])
    }
    return selected_columns
}
async function hidepanels() {
    request_link = 'http://' + location.host + "/get_allowed_panels/";
    response = await fetch(request_link).then(response => response.json());

    all_panels = response['all_panels'];
    panels = response['panels'];
    is_super_user = response['is_super_user']
    admin_panels = response['main_panels']['admin_panels'];
    main_panels = response['main_panels']



    if (is_super_user == '1') {
        document.getElementById('manage_users_tab').style.display = "block";
        for (i = 0; i < all_panels.length; i++) {
            panel = all_panels[i];
            try {
                document.getElementById(panel).style.display = "block";
            } catch {}
        }
        for (main_panel in main_panels) {
            try {
                document.getElementById(main_panel).style.display = "block";
            } catch {}
        }
        return;
    }
    // document.getElementById('books_analysis').style.display = "none";


    for (i = 0; i < all_panels.length; i++) {
        panel = all_panels[i];
        try {
            if (panels.includes(panel)) {
                document.getElementById(panel).style.display = "block";
            } else {
                document.getElementById(panel).style.display = "none";
            }
        } catch {}
    }

    for (main_panel in main_panels) {
        try {
            if (main_panels[main_panel].length != 0) {
                document.getElementById(main_panel).style.display = "block";
            }
        } catch {}
    }
}

hidepanels();

async function UserLog()
{
    if (getCookie("username") !== "") {
        const user_name = getCookie("username")
        let page_url = window.location.pathname
        const user_ip = "127.0.0.0"

        page_url = page_url.slice(0, -1);
        if(page_url==="")
        {
            page_url = "/0";
        }



        let form_data = new FormData()
        let detail_json = "نمایش پنل"

        form_data.append('detail_json', detail_json);
        let link_request = 'http://' + location.host + "/UserLogSaved/" + user_name + page_url + "/"+ user_ip + "/";


        $.ajax({
            url: link_request,
            data: form_data,
            contentType: false,
            processData: false,
            async: true,

        }).done(function (res) {
            console.log("done")

        }).fail(function (res) {
            console.log("fail")
        });


        // const request_link = 'http://' + location.host + "/UserLogSaved/" + user_name + page_url + "/"+ user_ip["ip"] + "/";
        // await fetch(request_link).then(response => response.json());
    }
}

UserLog ()
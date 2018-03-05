function saveComment(e) {
    e.preventDefault();
    var arr = $(this).serializeArray();
    console.log(arr);
    var json_arr = JSON.stringify(arr);
    console.log(json_arr);

    $.ajax({
        type: 'POST',
        dataType: 'json',
        contentType: 'application/json; charset=utf-8',
        url: '/save_comment',
        data: arr,
        success: function (data) {
            console.log('success', data);
        },
        error: function (data, jqXHR, textStatus, errorThrown) {
            console.log(data, jqXHR, textStatus, errorThrown);
        }
    });
}

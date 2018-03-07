function comment_action_success(data) {
    $(".commentActionResult p").text(data.msg);
    $(".commentActionResult p").fadeIn(500);
    $(".commentActionResult p").fadeOut(2000);
}

function comment_action_error(data) {
    $(".commentActionResult p").text(data.msg);
    $(".commentActionResult p").fadeOut(2000);
    $(".commentActionResult p").fadeOut(2000);
}


function saveComment(e) {
    e.preventDefault();
    var arr = $(this).serializeArray();
    console.log(arr);
    // var json_arr = JSON.stringify(arr);

    $.ajax({
        type: 'POST',
        dataType: 'json',
        contentType: 'application/json; charset=utf-8',
        url: '/save_comment',
        data: arr,
        success: function (data) {
            comment_action_success(data)
        },
        error: function (data, jqXHR, textStatus, errorThrown) {
            console.log(data, jqXHR, textStatus, errorThrown);
            comment_action_error(data)
        }
    });
}

function deleteComment(e) {
    e.preventDefault();
    var arr = $(this).serializeArray();
    // var json_arr = JSON.stringify(arr);

    $.ajax({
        type: 'POST',
        dataType: 'json',
        contentType: 'application/json; charset=utf-8',
        url: '/delete_comment',
        data: arr,
        success: function (data) {
            if (data.deleted_comment_id.length >= 1 && data.deleted_comment_id[0] != '') {
                $.each(data.deleted_comment_id, function (i, v) {
                    $('#row_id_' + v).remove();
                });
                comment_action_success(data);
            }
        },
        error: function (data, jqXHR, textStatus, errorThrown) {
            console.log(data, jqXHR, textStatus, errorThrown);
            comment_action_error(data)
        }
    });
}

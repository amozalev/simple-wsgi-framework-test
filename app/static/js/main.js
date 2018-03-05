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
            $("#saveCommentResult p").text(data.msg);
            $("#saveCommentResult p").fadeIn(500);
            $("#saveCommentResult p").fadeOut(2000);
        },
        error: function (data, jqXHR, textStatus, errorThrown) {
            console.log(data, jqXHR, textStatus, errorThrown);
            $("#saveCommentResult p").text('При сохранении возникла ошибка');
            $("#saveCommentResult p").fadeOut(2000);
            $("#saveCommentResult p").fadeOut(2000);
        }
    });
}

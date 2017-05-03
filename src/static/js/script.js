$(function() {
    $(document).on('change', ':file', function() {
        var form_data = new FormData($('#upload-file')[0]);
        $.ajax({
            type: 'POST',
            url: '/uploadFile',
            data: form_data,
            contentType: false,
            processData: false,
            //cache: false,
            //async: false,
            success: function(response) {
                var obj = JSON.parse(response)
                var arr = $.map(obj, function(el) { return el });
                document.getElementById('uploaded').innerHTML += '<div class="uploaded" id="file'+(arr.length-1)+'"><h4>'+arr[arr.length-1]+'</h4><button class="uploaded-remove" type="button" onclick="ajax_remove(\''+arr[arr.length-1]+'\', \'file'+(arr.length-1)+'\')">[x]</button></div>';
            },
            error: function(error){
            	alert(error);
            }
        });
    });
});

function ajax_remove(data, id){
    $.ajax({
        type: 'POST',
        url: '/removeFile',
        data: JSON.stringify(data),
        contentType: 'application/json;charset=UTF-8',
        processData: false,
        success: function(response) {
            $("#"+id).remove(); 
        },
        error: function(error){
        	alert(error);
        }
    });
}
UPLOAD_FOLDER = "../static/files/"

function showContents(student=''){
    $.ajax({ url: "/showContents",
        type: 'GET',
        contentType: 'application/json;charset=UTF-8',
        processData: false,
        success: function(response){
            var obj = JSON.parse(response)
            var arr = $.map(obj, function(el) { return el });
            document.getElementById('uploaded').innerHTML = '';
            for (i=1;i<arr.length; i++){
                if (arr[i].substring(arr[i].length - 4) != '.jpg'){
                    document.getElementById('uploaded').innerHTML += '<div class="uploaded" id="file'+(i+1)+'"><img class="thumb" src="'+UPLOAD_FOLDER+arr[i].substring(0, arr[i].length-4)+'.jpg"><h4 class="uploaded-file">'+arr[i]+'</h4><div class="uploaded-student">'+student+'</div><button class="uploaded-remove" type="button" onclick="ajax_remove(\''+arr[i]+'\', \'file'+(i+1)+'\')">[x]</button></div>';    
                }
            }
        },
        error: function(error){
            alert("error");
        }
    });
}

$(document).ready(function(){
    showContents();
});

$(document).on('change', ':file', function() {
    var form_data = new FormData($('#upload-file')[0]);
    $.ajax({
        type: 'POST',
        url: '/uploadFile',
        data: form_data,
        contentType: false,
        dataType: 'json',
        processData: false,
        //cache: false,
        //async: false,
        success: function(response) {
            showContents(response[1]);
        },
        error: function(error){
        	alert(error);
        }
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
            showContents();
        },
        error: function(error){
        	alert(error);
        }
    });
}
UPLOAD_FOLDER = "../static/files/"

function showContents(student=''){
    $.ajax({ url: "/showContents",
        type: 'GET',
        contentType: 'application/json;charset=UTF-8',
        processData: false,
        success: function(response){
            var obj = JSON.parse(response);
            var projects = $.map(obj, function(el) { return el });
            var students = projects.splice(0, projects.length/2);
            document.getElementById('uploaded').innerHTML = '';
            for (i=1;i<projects.length; i++){
                if (projects[i].substring(projects[i].length - 4) != '.jpg'){
                    document.getElementById('uploaded').innerHTML += '<div class="uploaded" id="file'+(i+1)+'"><img class="thumb" src="'+UPLOAD_FOLDER+students[i]+'-'+projects[i].substring(0, projects[i].length-4)+'.jpg"><h4 class="uploaded-file">'+projects[i].substring(0, projects[i].length-4)+'</h4><div class="uploaded-student">'+students[i]+'</div><button class="uploaded-remove" type="button" onclick="ajax_remove(\''+students[i]+'-'+projects[i]+'\', \'file'+(i+1)+'\')">[x]</button></div>';    
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

$("#preview").click(function() {
    $.ajax({
        type: "GET",
        url: "/preview",
        contentType: false,
        dataType: 'json',
        processData: false,
        success: function(response) {
            console.log(response);
        },
        error: function(result) {
            alert('error');
        }
    });
});
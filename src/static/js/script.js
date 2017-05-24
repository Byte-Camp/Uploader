UPLOAD_FOLDER = "../static/files/"

function showContents(){
    $.ajax({ url: "/showContents",
        type: 'GET',
        contentType: 'application/json;charset=UTF-8',
        processData: false,
        success: function(response){
            var obj = JSON.parse(response);
            var projects = $.map(obj, function(el) { return el });
            var students = projects.splice(0, projects.length/2);
            document.getElementById('uploaded').innerHTML = ''; file_ext = 4;
            for (i=0;i<projects.length; i++){
                if (projects[i].substring(projects[i].length - 4) != '.jpg'){              //file id for remove                         thumbnail                                                                                                        uploaded file or directory                                                       students name
                    if (projects[i].substring(projects[i].length - 4, projects[i].length - 3) != '.') { file_ext = 0; }
                    document.getElementById('uploaded').innerHTML += '<div class="uploaded" id="file'+(i+1)+'"><img class="thumb" src="'+UPLOAD_FOLDER+students[i]+'-'+projects[i].substring(0, projects[i].length-file_ext)+'.jpg"><h6 class="uploaded-file">'+projects[i]+'</h6><div class="uploaded-student">'+students[i]+'</div><button class="uploaded-remove" type="button" onclick="ajax_remove(\''+students[i]+'-'+projects[i]+'\', \'file'+(i+1)+'\')">X</button></div>';    
                }
            }
        },
        error: function(error){
            alert(error);
        }
    });
}

$(document).ready(function(){
    showContents();
});

$(document).on('change', ':file', function() {
    var url = '/uploadFile'
    var form_data = new FormData($('#upload-file')[0]);
    if (this.id == 'dir'){ url = '/uploadDirectory' }
    $.ajax({
        type: 'POST',
        url: url,
        data: form_data,
        contentType: false,
        dataType: 'json',
        processData: false,
        //cache: false,
        //async: false,
        success: function(response) {
            showContents();
            //document.getElementById("upload-file").reset();
            console.log(response);
        },
        error: function(error){
        	alert(error);
        }
    });
});

function ajax_remove(data, id){
    var result = confirm("Are you sure you want to delete?");
    if (result) {
        $.ajax({
            type: 'POST',
            url: '/removeFile',
            data: JSON.stringify(data),
            contentType: 'application/json;charset=UTF-8',
            processData: false,
            success: function(response) {
                showContents();
                console.log(response);
            },
            error: function(error){
                alert(error);
            }
        });
    }  
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
        error: function(error) {
            alert(error);
        }
    });
});
// JavaScript File to add event handlers
/* global $ sendInfo progressive_enhancement_on */

// $('#dept').change(function() {
//     if (progressive_on) {
//         event.preventDefault();

//         var dept = $('#dept :selected').text();
        
//         $.post(URL,{'dept':dept},update,'json');
//     }
// })

$('select[name="departments"]').change(function() {
    var dept = $(this).val();
    $.post(URL,{'dept':dept},update);
})

function update(obj) {
    console.log(obj)
    if(obj.error) {
        $('#errors').empty().html('Error:'+obj.err);
    } else {
        $('#nums').empty();
        var options = obj.nums;
        console.log(options)
        for (var i=0;i<options.length;i++){
            $('<option/>').val(options[i][0]).html(options[i][0]).appendTo('#nums');
         }
        console.log(obj)
    }
}

$("input[type=checkbox]").on('change', function() {
    bid = $('[name=bookid').val();
    
    if (this.checked) {
        sendSoldStatus(1,bid);
    } else {
        sendSoldStatus(0,bid);
    }
});

// Send sold status and book id to the backend
function sendSoldStatus(sold_status, book_id){
    $.post(URL,{'sold_status': sold_status, 'id': book_id}, addToPage);
}

// Display the updated sold status on the page
function addToPage(json_data){
    if (json_data['sold_status'] == 0) {
        $("#sold_status").text("Available");
    }
    else {
        console.log($('#sold_status').val())
        $("#sold_status").text("Sold");
    }
}
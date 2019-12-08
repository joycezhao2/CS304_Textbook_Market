// JavaScript File to add event handlers
/* global $ sendInfo progressive_enhancement_on */

$('#dept').on("click",function() {
    if (progressive_enhacement) {
        event.precentDefault();

        var dept = $(this).val();
        
        $.post(URL,{'dept':dept,'nums':0},updateN,'json');
    }
})

$('#num').on("click",function() {
    if (progressive_enhacement) {
        event.preventDefault();

        var dept = $('#dept').val();
        var num = $(this).val();

        $.post(URL,{'dept':dept,'nums':num},updateB,'json');
    }
})

function updateN(obj) {
    console.log(obj)

    if(obj.error) {
        $('#errors').empty().html('Error:'+obj.err);
    } else {
        $("#num").val(obj.nums)
        console.log(obj)
    }
}

function updateB(obj) {
    console.log(obj)

    if(obj.error) {
        $('#errors').empty().html('Error:'+obj.err);
    } else {
        $("#book-list").val(obj.books)
        console.log(obj)
    }
}

$("input[type=checkbox]").on('change', function() {
    console.log('checked!!!')
    bid = $('[name=bookid').val();
    console.log(bid);
    if (this.checked) {
        sendSoldStatus(1,bid);
    } else {
        sendSoldStatus(0,bid);
    }
    
    // if (this.checked) {
    //     sendSoldStatus(1,bid)
    // }
    // else {
    //     sendSoldStatus(0,bid)
    // }
});

// Send sold status and book id to the backend
function sendSoldStatus(sold_status, book_id){
    console.log("inside sendSoldStatus");
    console.log(book_id);
    console.log(sold_status);
    $.post(URL,{'sold_status': sold_status, 'id': book_id}, addToPage);
}

// Display the updated sold status on the page
function addToPage(json_data){
    console.log("inside addToPage");
    if (json_data['sold_status'] == 0) {
        $("#sold_status").text("Available");
    }
    else {
        console.log($('#sold_status').val())
        $("#sold_status").text("Sold");
    }
}
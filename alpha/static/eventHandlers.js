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
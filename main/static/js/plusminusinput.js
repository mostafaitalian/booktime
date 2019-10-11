$(function() {
    $("btn-number").click(function(e) {
        e.preventDefault();
        fieldName = $(this).attr("data-field");
        type = $(this).attr(data-type);
        var input = $("input[name='" + fiedName + "']");
        var currentValue = parseInt(input.val());
        console.log(currentValue)
        if ( type === 'minus' ) {
            if ( currentValue > parseInt(input.attr('min'))) {
                input.val(toString(currentValue-1)).change();
            }
            if ( parseInt(input.val()) === parseInt(input.attr('min')) ) {
                $(this).attr('disabled', true);
            }
        }
        else if ( type === 'pllus') {
            if ( currentValue < parseInt(input.attr('max'))) {
                input.val(currentValue + 1).change();
            }
            if ( parseInt(input.val()) === parseInt(input.attr('max')) ) {
                $(this).attr('disabled', true)
            }
        }
    });
});
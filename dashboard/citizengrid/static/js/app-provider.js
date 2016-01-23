
$(function() {

<!-- MODAL TREE STRUCTURE -->

    //$("li.parent-list ul").hide(); //hide the child lists
    $("li.parent-list i").click(function () {
        $(this).toggleClass('icon-caret-up icon-caret-down'); // toggle the font-awesome icon class on click
        $(this).next("ul").toggle(); // toggle the visibility of the child list on click
    });

<!--MODAL MULTISELECT FUNCTIONALITY -->

// check-uncheck all
    $(document).on('change', 'input[id="all"]', function () {
    console.log("child")
        $('.canine').prop("checked", this.checked);
    });

// parent/child check-uncheck all
    $(function () {
        $('.parent').on('click', function () {
        console.log("parent")
            $(this).closest('ul li').find(':checkbox').prop('checked', this.checked);
        });
    });


});

// Activate the info tooltips in the wizard
$(document).ready(function() {
	$('body').tooltip({
	    selector: '.wizard-field-info'
	});
});
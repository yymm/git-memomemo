var global_lock_check_status;

$(document).ready( function()
{
	$('.memo-input-title').val("");
	$('.memo-input-text').val("");
	$('.memo-input-tag').val("");
	$('.particle-switch').attr('checked', false);
	$('#lock-check').attr('checked', false);
	global_lock_check_status = false;
});

$('.memo-edit').click( function()
{
	var title = $(this).closest('dd').find('.memo-title-only').text();
	var text = $(this).closest('dd').find('.memo-text').text();
	var tag = $(this).closest('dd').find('.memo-tag').text();
	$('.memo-input-title').val(title);
	$('.memo-input-text').val(text);
	$('.memo-input-tag').val(tag);
	show_addentry();
	return false;
});

$('.particle-switch').click( function()
{
	if (this.checked)
	{
		$('.draw').css('display', 'inline-block');
		$('#title-img').css('display', 'none');
	}
	else
	{
		$('.draw').css('display', 'none');
		$('#title-img').css('display', 'block');
		$('#title-img').css('text-align', 'center');
		$('#title-img').css('margin', '-0.7em');
	}
});

$('#lock-check').click( function()
{
	global_lock_check_status = this.checked;
	if (this.checked)
	{
		show_addentry();
	}
});

var show_addentry = function()
{
	$('.addentry-div').css('margin', '2em 0em 2em 0em');
	$('.addentry-div').css('width', '30em');
	$('.addentry-div').css('height', '30em');
	$('.addentry-div').css('top', '10em');
	$('.addentry-div').css('border', '5px solid, #ccc');
	$('.addentry-div').css('padding', '0.8em');
	$('.addentry-div').css('background', '#333333');
	$('.addentry-div').css('position', 'fixed');
	$('.addentry-div').css('border-radius', '20px');
	$('.addentry-div').css('z-index', '50');
	$('.addentry-div form').css('display', 'inline-block');
	$('.addentry-div form').css('width', '25em');
	$('.addentry-div form').css('height', '25em');
	$('.addentry-div form').css('font-size', '1.0em');
	$('.addentry-div img').css('display', 'none');
};

var hide_addentry = function()
{
	$('.addentry-div').css('margin', '2em 0em 2em 0em');
	$('.addentry-div').css('width', '2em');
	$('.addentry-div').css('height', '2em');
	$('.addentry-div').css('border', '5px solid, #ccc');
	$('.addentry-div').css('padding', '0em');
	$('.addentry-div').css('background', '#4d4d4d');
	$('.addentry-div').css('position', 'fixed');
	$('.addentry-div').css('border-radius', '20px');
	$('.addentry-div form').css('display', 'none');
	$('.addentry-div img').css('display', 'block');
};

$('.addentry-div').hover( function()
{
	show_addentry();
},
function ()
{
	if (global_lock_check_status == false)
	{
		hide_addentry();
	}
});

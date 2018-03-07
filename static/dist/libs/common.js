window.onload = function() {

	//new Slider('#credit-slider-1', 750, 10000);

	//new Slider('#termin-slider-1', 56, 99);

	//new Slider('#credit-slider-2', 750, 10000);

	//new Slider('#termin-slider-2', 1, 12);

	//new Slider('#credit-slider-3', 750, 10000);

	//new Slider('#termin-slider-3', 1, 12);

	sliderFiller();


	/*#Slick slider*/

	$('.s-packages-content').slick({
		dots: true,
		infinite: false,
		speed: 300,
		slidesToShow: 4,
		responsive: [
		{
			breakpoint: 1041,
			settings: {
				slidesToShow: 2,
				slidesToScroll: 2
			}
		}]
	});

	$('.b-response-wrap').slick({
		dots: true,
		speed: 300,
		slidesToScroll: 1,
		slidesToShow: 3,
		responsive: [
		{
			breakpoint: 1041,
			settings: {
				slidesToShow: 2,
				slidesToScroll: 2
			}
		}]
	});

	/*#Review change*/

	$('.b-review__person').on('click', function(e) {
		$('.b-review__person').not($(this)).removeClass('active');
		$(this).addClass('active');

		var personId = $(this).attr('id');

		var arr = personId.split("-");

		$('.b-review__info p').removeClass('active');

		$('#review-' + arr[1]).addClass('active');

	});


	/*#Choose plan*/

	$('.b-section-message__item').on('click', function(e) {
		$('.b-section-message__item').removeClass('active')
		$(this).addClass('active');
	});


	/*#Cities list func*/
	
	$('.b-region-list__wrapper').on('click', '.b-region-list__btn', function(e) {
		var dep_id = $(this).data('dep_id');

		fieldFiller(dep_id, "/ajax/departments_generate/" + dep_id);  //"/static/data-city.json");
		$('.b-region-list__btn').removeClass('btn-active');
		$(this).addClass('btn-active');

		var listItems = $(this).parent().parent().html();

		$('.popup-list').html(listItems);
		
		$('.b-region-list').animate({
			opacity: "0"
		}, 500, function(){
			$('.b-region-list').css('z-index', '-1');
			$('.popup').css('z-index', '100').animate({opacity: '1'}, 500);
		});
	});

	$('.btn-show').on('click', function() {
		$('.popup').animate({opacity: '0'}, 500, function(){
			$('.b-region-list__btn').removeClass('btn-active');
			$('.popup').css('z-index', '-1');
			$('.b-region-list').css('z-index', '1').animate({opacity: 1}, 300);
		});
	});

	/*#Accordion*/

	$('.b-spoiler-title').on('click', function(e) {
		$('.b-spoiler-title').not($(this)).removeClass('active');
		$(this).toggleClass('active');
	});

	$('.b-btn--secondary').on('click', tabs);

	$('.b-vacancies__tab').on('click', tabs);

	$('.s-head__nav-btn').on('click', tabs);

	$('.support-btn').on('click', tabs);

	$('.message').on('click', tabs);

	/*#Pagination*/

	$('.b-blog-nav__btn').on('click', function(){
		if($(this).hasClass('active')) return;
		$('.b-blog-nav__btn').removeClass('active');
		$(this).addClass('active');
		pagination();
	});

	$('.b-blog-nav__btn-next').on('click', function() {
		var currentBtn = $('.b-blog-nav__btn.active');
		if (currentBtn.next().hasClass('b-blog-nav__btn')) {
			var nextBtn = currentBtn.next();
		} else {
			var nextBtn = $('.b-blog-nav__btn:first');
		}

		currentBtn.removeClass('active');
		nextBtn.addClass('active');

		pagination();
	});

	$('.b-blog-nav__btn-prev').on('click', function() {
		var currentBtn = $('.b-blog-nav__btn.active');

		if (currentBtn.prev().hasClass('b-blog-nav__btn')) {
			var nextBtn = currentBtn.prev();
		} else {
			var nextBtn = $('.b-blog-nav__btn:last');
		}

		currentBtn.removeClass('active');
		nextBtn.addClass('active');
		pagination();
	});

	/*#Redacting*/

	var inp = $('.profile__input input');

	$('.profile__input label').on('click', function(e) {
		inp.attr('disabled', false);
	});

	inp.focusout(function() {
		$(this).attr('disabled', true);
	});

	/*#Add files*/

	$('input[type=file]').on('change', function(e) {
		var reader = new FileReader();

		for (var i = 0; i < e.originalEvent.srcElement.files.length; i++) {
			var file = e.originalEvent.srcElement.files[i];
			var img = document.createElement("img");
			var div = document.createElement('div');
			div.classList.add('profile__doc');
			var title = document.createElement('h3');
			title.classList.add('profile__doc-title');
			title.innerHTML = fileName;

			var _tempArr = $(this).val().split('\\').pop()
			.split('.');
			var fileName = _tempArr[0];

			title.innerHTML = fileName;

			var reader = new FileReader();

			reader.onloadend = function() {
				img.src = reader.result;
			}

			reader.readAsDataURL(file);
			$(this).parent().parent().before(div);
			div.append(img);
			div.append(title);	
		}
	});

	/*#Form popup*/

	$('.application-add').on('click', function(e) {
		$('.overlay').addClass('active');
		$('.overlay').children().css('opacity', '0').animate({
			opacity: 1
		}, 300);
		$('.blur').addClass('active');
	});

	$('.overlay').on('click', function(e){
		formFadeOut(e, $('.b-main-form--popup'), $('.overlay'), $('.blur'));
	});

	$('.b-main-form--popup .b-btn-primary').on('click', function(e) {
		e.preventDefault();

		$('.b-main-form--popup').fadeOut(function() {
			$('.f-form').css({
				display: 'block',
				opacity: 0
			}).animate({
				opacity: 1
			}, 300);
		});
	});

	$('.f-form #cancel').on('click',  function() {
		$('.f-form').fadeOut(function() {
			$('.b-main-form--popup').css({
				display: 'flex'
			}).animate({
				opacity: 1
			},400)
		})
	});
}

function formFadeOut(e, form, overlay, blur) {
	if (!e.target.classList.contains('active')) return;

	overlay.children().animate({opacity: 0}, 300, function(e) {
		overlay.removeClass('active');
		blur.removeClass('active');
	});
}

function pagination() {
	var dataCount= $('.b-blog-nav__btn.active').data('blogbtn');;
	var currentContent = $('.b-blog-container');
	var dataContent = $('[data-container=' + dataCount + ']');

	currentContent.stop(true, true).animate({
		opacity: 0
	},300, function() {

		currentContent.css({display: 'none'});

		dataContent.css({
			display: 'flex',
			opacity:0
		}).animate({
			opacity: 1
		}, 300);
	});
};

function Slider(initialId, min, max) {

	if (document.querySelector(initialId) == null) return;

	var arr = initialId.split("-");
	var id = arr[2];
	var kind = arr[0];

	var sliderValue = $(kind + "-value-" + id);
	var sliderTotal = $(kind + "-total-" + id);
	var sliderHandle = $(initialId + ' .ui-slider-val');
	var quantity = sliderHandle.html().split(" ")[1];

	$(initialId).slider({
		min: min,
		max: max,
		range: "min",
		animate: "slow",
		slide: function( event, ui) {
			sliderValue.val(ui.value);
			sliderHandle.html(ui.value + ' ' + quantity);
			sliderTotal.html(ui.value + ' ' + quantity);
		}
	});

	sliderValue.val( $(initialId).slider("value") );

	sliderValue.change(function(){
		var value = $(this).val();
		$(initialId).slider("value", value);
		sliderHandle.html(value + ' ' + quantity);
		sliderTotal.html(value + ' ' + quantity);
	});
}

function fieldFiller (dep_id, url) {

	$.ajax({
		url: url,
		success: function(data) {
			for(key in data) {
				if (parseInt(key) === parseInt(dep_id)) {	
					$('#data-map').attr('src', data[key].link);			
					$('#data-adress').html(data[key].address);
					$('#data-city').html(data[key].city);
					$('#data-localAdress').html(data[key].address);
					$('#data-schedule').html(data[key].schedule);
					$('#data-mail').html(data[key].email).attr('href',
						'mailto:'+ data[key].email);
					$('#data-phone').html(data[key].phone).attr('href',
						'tel:' + data[key].phone);
				}
			}
		}
	});

}


function sliderFiller(){
	$.ajax({
		url:'/ajax/slider_filler/',
		success: function(data){
			for(key in data){
				new Slider('#credit-slider-' + key, data[key].sum_min, data[key].sum_max);
				new Slider('#termin-slider-' + key, data[key].term_min, data[key].term_max);
			}
		}
	})
}

function tabs() {
	var dataBtn = $(this).data('btn');
	var content = $('[data-content=' + dataBtn + ']');
	var currentContent = $('.tab-content');
	var clName = '.' + this.className.split(' ')[0];

	if ($(content).hasClass('is-showed')) return;

	$(clName).removeClass('active');
	$(this).addClass('active');

	currentContent.stop(true, true).animate({
		opacity: 0
	}, 300 , function() {
		currentContent.removeClass('is-showed');

		content.addClass('is-showed').animate({
			opacity: 1
		}, 300);
	});
}
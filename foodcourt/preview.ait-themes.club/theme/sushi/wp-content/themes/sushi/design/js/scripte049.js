/*
 * AIT WordPress Theme
 *
 * Copyright (c) 2012, Affinity Information Technology, s.r.o. (http://ait-themes.com)
 */
/* Main Initialization Hook */
jQuery(document).ready(function(){
	gm_authFailure = function(){
		var apiBanner = document.createElement('div');
		var a = document.createElement('a');
		var linkText = document.createTextNode("Read more");
		a.appendChild(linkText);
		a.title = "Read more";
		a.href = "https://www.ait-themes.club/knowledge-base/google-maps-api-error/";
		a.target = "_blank";

		apiBanner.className = "alert alert-info";
		var bannerText = document.createTextNode("Please check Google API key settings");
		apiBanner.appendChild(bannerText);
		apiBanner.appendChild(document.createElement('br'));
		apiBanner.appendChild(a);

		jQuery(".google-map-container").html(apiBanner);
	};

	/* menu.js initialization */
	desktopMenu();
	responsiveMenu();
	/* menu.js initialization */

	/* portfolio-item.js initialization */
	portfolioSingleToggles();
	/* portfolio-item.js initialization */

	/* custom.js initialization */
	renameUiClasses();
	removeUnwantedClasses();

	initWPGallery();
	initColorbox();
	initRatings();
	//initInfieldLabels();
	initSelectBox();

	notificationClose();
	/* custom.js initialization */

	/* Theme Dependent Functions */
	//aitWcProductVariationsFormSelectsResetFix();
	/* Theme Dependent Functions */
});
/* Main Initialization Hook */

/* Theme Dependenent Functions */
/* Theme Dependenent Function */

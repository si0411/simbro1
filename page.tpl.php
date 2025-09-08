<?php
/**
 * @file
 * Default theme implementation to display a single Drupal page.
 *
 * The doctype, html, head and body tags are not in this template. Instead they
 * can be found in the html.tpl.php template in this directory.
 *
 * Available variables:
 *
 * General utility variables:
 * - $base_path: The base URL path of the Drupal installation. At the very
 *   least, this will always default to /.
 * - $directory: The directory the template is located in, e.g. modules/system
 *   or themes/bartik.
 * - $is_front: TRUE if the current page is the front page.
 * - $logged_in: TRUE if the user is registered and signed in.
 * - $is_admin: TRUE if the user has permission to access administration pages.
 *
 * Site identity:
 * - $front_page: The URL of the front page. Use this instead of $base_path,
 *   when linking to the front page. This includes the language domain or
 *   prefix.
 * - $logo: The path to the logo image, as defined in theme configuration.
 * - $site_name: The name of the site, empty when display has been disabled
 *   in theme settings.
 * - $site_slogan: The slogan of the site, empty when display has been disabled
 *   in theme settings.
 *
 * Navigation:
 * - $main_menu (array): An array containing the Main menu links for the
 *   site, if they have been configured.
 * - $secondary_menu (array): An array containing the Secondary menu links for
 *   the site, if they have been configured.
 * - $breadcrumb: The breadcrumb trail for the current page.
 *
 * Page content (in order of occurrence in the default page.tpl.php):
 * - $title_prefix (array): An array containing additional output populated by
 *   modules, intended to be displayed in front of the main title tag that
 *   appears in the template.
 * - $title: The page title, for use in the actual HTML content.
 * - $title_suffix (array): An array containing additional output populated by
 *   modules, intended to be displayed after the main title tag that appears in
 *   the template.
 * - $messages: HTML for status and error messages. Should be displayed
 *   prominently.
 * - $tabs (array): Tabs linking to any sub-pages beneath the current page
 *   (e.g., the view and edit tabs when displaying a node).
 * - $action_links (array): Actions local to the page, such as 'Add menu' on the
 *   menu administration interface.
 * - $feed_icons: A string of all feed icons for the current page.
 * - $node: The node object, if there is an automatically-loaded node
 *   associated with the page, and the node ID is the second argument
 *   in the page's path (e.g. node/12345 and node/12345/revisions, but not
 *   comment/reply/12345).
 *
 * Regions:
 * - $page['help']: Dynamic help text, mostly for admin pages.
 * - $page['highlighted']: Items for the highlighted content region.
 * - $page['content']: The main content of the current page.
 * - $page['sidebar_first']: Items for the first sidebar.
 * - $page['sidebar_second']: Items for the second sidebar.
 * - $page['header']: Items for the header region.
 * - $page['footer']: Items for the footer region.
 *
 * @see bootstrap_preprocess_page()
 * @see template_preprocess()
 * @see template_preprocess_page()
 * @see bootstrap_process_page()
 * @see template_process()
 * @see html.tpl.php
 *
 * @ingroup themeable
 */
?>

<header id="navbar" role="banner">

	<div class="navbar-main-block custom-top1">

		<div class="navbar-block navbar-fixed-top navbar-default custom-navb">

			<div class="container">

				<div class="row">

					<div class="navbar-header">

						<button aria-expanded="false" aria-controls="bs-navbar" data-target="#bs-navbar" data-toggle="collapse" type="button" class="navbar-toggle collapsed">

	        			<span class="sr-only">Menu</span>

	        			<span class="icon-bar top-bar"></span>

	        			<span class="icon-bar middle-bar"></span>

	        			<span class="icon-bar bottom-bar"></span>

	      				</button>

						

							<?php if ($logo): ?>

							  <a class="navbar-brand" href="<?php print $front_page; ?>" title="<?php print t('Home'); ?>">

								<img src="<?php print $logo; ?>" alt="<?php print t('Home'); ?>" />

							  </a>

							  <?php endif; ?>



							  <?php if (!empty($site_name)): ?>

							  <a class="name navbar-brand" href="<?php print $front_page; ?>" title="<?php print t('Home'); ?>"><?php print $site_name; ?></a>

							  <?php endif; ?>

						

					</div>



						<?php if (!empty($primary_nav) || !empty($secondary_nav) || !empty($page['navigation'])): ?>

							<nav class="collapse navbar-collapse tour-navbar" id="bs-navbar">

							  <?php if (!empty($primary_nav)): ?>

								<?php print render($primary_nav); ?>

							  <?php endif; ?>

							</nav>

						<?php endif; ?>

						

				</div>

			</div>

		</div>

	</div>

	<!--slider block-->

	<div class=" banner-block2">

		<?php print render($page['slider']); ?>

		<?php global $base_url; global $user;?>

		<?php if (!empty($page['top_carousel'])): ?>

			<?php print render($page['top_carousel']); ?>

		<?php else: ?>
                        <img src="<?php print $base_url;?>/sites/backpackingthroughcambodia.com/themes/cambodia/assets/images/Header_otherpages_BTC.jpg">
		<?php endif; ?>

	</div>

	<!--Slider block ends-->

</header>

<section<?php print $cur_currency_class; ?>>

	<div class="main-section2">

		<div class="container">

			<div class="row">

				<div class="main-inner-section2 blog-page" data-sticky_parent>

				    <div<?php print $content_column_class; ?> data-sticky_column id="sticky-col8">

				    	<?php 

				    		$curr_path = current_path();

				    		$acc_path = drupal_substr($curr_path, $start=0, $length=16);

					    	$tour_pages = array('additional-trips');

					    	if (in_array($acc_path, $tour_pages))

							{

								$class = "tours-dates";

							}

							else

							{

								$class = "";

							}

				    	?>

				    	<?php 

				    		$profile = drupal_substr($curr_path, $start=0, $length=8);

				    		if($profile == 'profile-')

				    		{$profile_class = 'profile-page-title';}

				    		elseif($profile == 'user')

				    			{$profile_class = 'account-login-section';}

				    	 ?>

				    	 	<div class="whats-included-block <?php if(isset($profile_class)):print $profile_class;endif;?>">

								<?php if (!empty($page['highlighted'])): ?>

									<div class="highlighted jumbotron"><?php print render($page['highlighted']); ?></div>

								<?php endif; ?>

								<!--?php if (!empty($breadcrumb)): print $breadcrumb; endif;?-->

								<a id="main-content"></a>

								<?php print render($title_prefix); ?>

								<?php 

									if (arg(0) == 'user' && arg(1) == 'password') {

									  $title = t('Reset Password');

									}else{

									  $title = $title;

									}

									

									

								?>

								<?php if (!empty($title)): ?>



									<h2 class="page-title-h2"><?php print $title; ?></h2>

								<?php endif; ?>

									<?php print render($title_suffix); ?>

									<?php print $messages; ?>

								<?php if (!empty($tabs)): ?>

									<?php print render($tabs); ?>

								<?php endif; ?>

								<?php if (!empty($page['help'])): ?>

									<?php print render($page['help']); ?>

								<?php endif; ?>

								<?php if (!empty($action_links)): ?>

									<ul class="action-links"><?php print render($action_links); ?></ul>

								<?php endif; ?>



								<?php print render($page['account-login-block']); ?>

								<div class="wrapper-two-blocks">

									<?php print render($page['checkout_block']); ?>

								</div>

								

								<?php if(isset($class)&& !empty($class)):?>

									<div class="<?php print $class;?>">

								<?php endif;?>

								<?php print render($page['content']); ?>

								<?php if(isset($class)&& !empty($class)):?>

									</div>

								<?php endif;?>



							</div>

					</div>

					<?php if (!empty($page['sidebar_second'])): ?>

							<div class="col-sm-4 col-md-4 Book-a-Week-block blog-sidebar" data-sticky_column>

							   <div class="sidebar">



													  

									<?php print render($page['sidebar_second']); ?>

								

								

							   </div>

							</div>

                            <?php endif; ?>

							

						

				</div>	

			</div>

		</div>	

	</div>

</section>





<footer>

	 <div class="col-md-12 footer-block">

	 	<div class="row">

			<div class="container">

				<?php print render($page['footer']); ?>

				<div class="select-wrap text-center">

					<?php print render($page['footer2']); ?>

				</div>

				<?php print render($page['footer3']); ?>

			</div>

		</div>

	 </div>

</footer>


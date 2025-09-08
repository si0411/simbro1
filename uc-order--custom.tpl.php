<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta name="viewport" content="width=device-width" />
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />


<style>
/* unvisited link */
a:link {
    color: #08a0d3 !important;
    text-decoration: none;
    font-weight: bold; 
}
/* visited link */
a:visited {
    color: #08a0d3 !important;
    text-decoration: none;
    font-weight: bold; 
}

/* mouse over link */
a:hover {
    color: #08a0d3 !important;
    text-decoration: none;
    font-weight: bold; 
}

/* selected link */
a:active {
    color: #08a0d3 !important;
    text-decoration: none;
    font-weight: bold;
    
}

a.blackstyle:link {color:#333333 !important;font-weight: normal;}
a.blackstyle:visited {color:#333333 !important;font-weight: normal;}
a.blackstyle:hover {color:#333333 !important;font-weight: normal;}
a.blackstyle:active {color:#333333 !important;font-weight: normal;}

table#t01{
    background-color: #ffffff;
    font-size:14px;
    font-family: Helvetica, Arial, sans-serif;   
    border-width: 0px;
    border-style: solid;
    border-collapse: collapse;
} 
td#t01, th#t01 {
	padding: 8px;
} 
</style>
</head>
<body bgcolor='#f4f4f4' style="color: rgb(33, 33, 33); margin:0; padding:0; font-size:13px; font-family: Helvetica, Arial, sans-serif;background:#f4f4f4;">
  <?php global $base_url; ?>
  <?php foreach ($products as $product): ?>
    <?php if(isset($product->data['attributes']['Payment Type'])): ?>
      <?php foreach ($product->data['attributes']['Payment Type'] as $key => $value): ?>
          <?php $pay_type = $product->data['attributes']['Payment Type'][$key]; ?>
      <?php endforeach; ?>
    <?php else: ?>
      <?php foreach ($product->data['attributes']['Nights'] as $key => $value): ?>
          <?php $pay_type = $product->data['attributes']['Nights'][$key]; ?>
      <?php endforeach; ?>
    <?php endif; ?>
  <?php endforeach; ?>

  <!-- Conditional Wrapper Class -->
  <?php 
    if(($pay_type == '(deposit)') || ($pay_type == '(full price)')){
      $conditional_class = 'deposit_full_payment';
    }elseif($pay_type == '(remaining)'){
      $conditional_class = 'remaining_balance';
    }else{
      $conditional_class = 'exrta_trip_accomodation';
    }
  ?>
  <!-- Code ends here -->
<table style="width:100%;>

	<tr style="height:20px;"><td></td></tr>
	<tr style="text-align:center;"><td><a style="text-decoration: none; display: inline;" href="http://www.backpackingthroughvietnam.com"> <img style="margin-bottom:2px; border:none; display:inline;"  src="[site:url]/sites/all/themes/btt/assets/images/Logo-Text_only_small.png" alt="Backpacking Through Vietnam"></a></td></tr>
	<tr style="height:15px;"><td></td></tr>	
	
</table>


<table style="width:100%; cellpadding:30; padding:10px; line-height:18px; table-layout:fixed;font-family: Helvetica, Arial, sans-serif; font-size:14px;">

<tr>
<td></td>
<td bgcolor="#ffffff" style="padding: 20px; text-align:left; width:95%; height:50px; background:#ffffff; border-radius: 0px; border:0px solid #f0f0f0;">
	<p>Hey <?php echo $order_first_name; ?>,<p/><br/>
	<p><?php if(($pay_type == '(deposit)') || ($pay_type == '(full price)')):?>
                  <p>Thank you for booking your tour with Backpacking Through Vietnam!</p> <br/>
                  <p>Please may use your email address and password to login to your<a href="<?php print $base_url;?>/account-overview"> account</a> to enter more information about yourself. Inside your account you can also arrange extra accommodation and trips during your time in Vietnam.</p><br/>
                  <p>You will be assigned a dedicated tour coordinator whose job it is to take care of you! So please feel free to ask any questions that you have on your mind. He or she will be in contact with you within 2 working days, please check your junk mail.</p>
                  <p>Please note: Please wait for a tour confirmation email from your tour coordinator before making any flight arrangements. </p>
                  <p>In the mean time, if you have any questions, check our <a href="<?php print $base_url;?>/faq">FAQ</a> page, message us on our <a href="https://www.facebook.com/backpackingthroughvietnam">Facebook page</a>, or get in touch via our <a href="<?php print $base_url;?>/content/contact-us">contact us</a> from our contact us page.</p> <br/>        
                <?php elseif($pay_type == '(remaining)'):?>
                  <p>Thank you for completing your payment!</p> <br/>
                <?php else:?>
                  <p>Thank you for booking with Backpacking Through Vietnam! Here is your booking information:</p></p> <br/>
		<?php endif; ?>
       
<table id="t01" cellspacing="10">
  <colgroup>
    <col span="1" style="background-color:#cccccc">
    <col style="background-color:#f5f5f5">
  </colgroup>
  
</br>
  <tr id="t01">
    <td id="t01">Name</td>
    <td id="t01"><?php print $order_first_name." ".$order_last_name; ?></td> 
  </tr>
  <tr id="t01">
      <td id="t01">Email</td>
    <td id="t01"><?php print $order_email; ?></td> 
  </tr>
    <tr id="t01">
    <td id="t01">Phone</td>
    <td id="t01"><?php print $uc_addresses_billing_phone; ?></td> 
  </tr>
    <tr id="t01">
      <td id="t01">Your booking</td>
    <td id="t01"> <?php if(($pay_type == '(deposit)') || ($pay_type == '(full price)')): ?>
                      <?php print drupal_ucfirst($pay_type); ?> - <?php print $product->qty; ?> x <?php print $product->title; ?> - <?php echo str_replace('.00', '', $order_total).' '.$product->currency; ?>
                    <?php elseif($pay_type == '(remaining)'): ?> 
                      <?php echo "Remaining Balance"; ?> - <?php print $product->qty; ?> x <?php print $product->title; ?> - <?php echo str_replace('.00', '', $order_total).' '.$product->currency; ?>
                    <?php elseif($pay_type == '(Price Per night)'): ?> 
                      <?php echo "Extra accommodation x ".$product->qty; ?>
                    <?php else:?>
                      <?php echo drupal_ucfirst($pay_type)."!"; ?>
                    <?php endif; ?></td> 
  </tr>
    <tr id="t01">
    <td id="t01">Booking Number</td>
    <td id="t01"><?php print strip_tags($order_link); ?></td>
  </tr>
  <tr id="t01">
      <td id="t01">Booking Date</td>
    <td id="t01"><?php print $order_created; ?></td> 
  </tr>
    <tr id="t01">
    <td id="t01">Total Payment</td>
    <td id="t01"><?php echo str_replace('.00', '', $order_total).' '.$product->currency; ?></td> 
  </tr>
    <tr id="t01">
      <td id="t01">Payment Method</td>
    <td id="t01">Paypal</td> 
  </tr>
</table>

	<p style="height:5px;"></p>
	<p>Kind Regards,</p>
	<p>Backpacking Through Vietnam</p>  <br/>				
<a style="text-decoration: none; display: inline;" href="http://www.backpackingthroughvietnam.com"> <img style="margin-bottom:2px; border:none; display: inline;width: 175px;height: 72px;"  src="[site:url]/sites/all/themes/btt/assets/images/btv-logo-mails.png" alt="Backpacking Through Vietnam"></a>
<br/>
<a style="text-decoration: none; display: inline;" class="social signature_facebook-target sig-hide" href="https://www.facebook.com/backpackingthroughvietnam"> <img width="35" style="margin-bottom:2px; border:none; display:inline;" height="35"  src="[site:url]/sites/all/themes/btt/assets/images/social-icons/facebookIcon.png" alt="Facebook"></a>
<a style="text-decoration: none; display: inline;" class="social signature_twitter-target sig-hide" href="https://twitter.com/BTThailand"><img width="35" style="margin-bottom:2px; border:none; display:inline;" height="35"  src="[site:url]/sites/all/themes/btt/assets/images/social-icons/twitterIcon.png" alt="Twitter"></a>
<a style="text-decoration: none; display: inline;" class="social signature_instagram-target sig-hide" href="https://www.instagram.com/backpackingvietnam"><img width="35" style="margin-bottom:2px; border:none; display:inline;" height="35"  src="[site:url]/sites/all/themes/btt/assets/images/social-icons/instagramIcon.png" alt="Instagram"></a>	
</td>
<td></td>

</table>

</body>
</html>
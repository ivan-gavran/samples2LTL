function hide_result() {
  $("#id_result_div").fadeOut("fast");
}

function show_result_success(title, html) {
   // Change class of div
  div = $("#id_result_div");
  div.hide();
  div.removeClass("alert-warning");
  div.removeClass("alert-danger");
  div.addClass("alert-success");

  // Update header      
  $("#id_result_header").html(title);

  // Update body
  $("#id_result_body").html(html);

  // Show result
  $("#id_result_div").fadeIn("fast");

}

function show_result_warning(title, html) {
  // Change class of div
  div = $("#id_result_div");
  div.hide();
  div.removeClass("alert-success");
  div.removeClass("alert-danger");
  div.addClass("alert-warning");

  // Update header      
  $("#id_result_header").html(title);

  // Update body
  $("#id_result_body").html(html);

  // Show result
  $("#id_result_div").fadeIn("fast");

}

function show_result_error(title, html) {
  // Change class of div
  div = $("#id_result_div");
  div.hide();
  div.removeClass("alert-warning");
  div.removeClass("alert-success");
  div.addClass("alert-danger");

  // Update header      
  $("#id_result_header").html(title);

  // Update body
  $("#id_result_body").html(html);

  // Show result
  $("#id_result_div").fadeIn("fast");

}

function normal_button() {
  $("#id_spinner").hide();
  $("#id_submit_label").text("Learn");
  $("#id_submit").prop("disabled", false);
}

function working_button() {
  $("#id_submit").prop("disabled", true );
  $("#id_submit_label").text("Working ...");
  $("#id_spinner").show();
}
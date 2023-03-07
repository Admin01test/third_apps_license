odoo.define('rma_portal_form_validation_ept', function (require) {
    "use strict";

    $(document).ready(function () {

    	
    	//if any checkbox is checked
    	function checkbox_validate()
    	{
    	 var anyBoxesChecked = false;
         
         $('.rma_form input[type="checkbox"]').each(function() {
             if ($(this).is(":checked")) {
                 anyBoxesChecked = true;
                 $("#btnsubmit").removeAttr("disabled")
                 $(".form_error_msg").css("display","none")
             }
             
         });
      
         if (anyBoxesChecked == false) {
           $("#btnsubmit").prop("disabled",true);
           $(".form_error_msg").css("display","block").html("Please select atleast one product.");
         } 
    	}
    	

    	checkbox_validate()
    	
    	
        //set Required Attribute to select and textbox when checkbox is Tick.
        $(".tick_box").on('change', function () {
            var ischecked = $(this).is(":checked");
            
            if (ischecked) {
                $(this).parent().siblings().find("select").attr("required","true")
                $(this).parent().siblings().find("input[type=text]").attr("required","true")
                $("#btnsubmit").removeAttr("disabled")
                 $(".form_error_msg").css("display","none")
               
            }else{
                $(this).parent().siblings().find("select").removeAttr("required")
                $(this).parent().siblings().find("input[type=text]").removeAttr("required")
              
            }
        });

        //some Validations for Return Quantity
        $(".return_qty").keyup(function () {
            var return_qty = parseInt($(this).val());
            var delivered_qty = parseInt($(this).parents("div.col-sm-2.text-center").siblings().find("#delivered_qty").val());

            checkbox_validate()
            
            if (return_qty == 0){
            	$(this).val(1);
                }
            if (return_qty < 0){
            	
            	  $(this).parents("div.col-sm-2.text-center").siblings().find("input[type=checkbox]").prop("checked", false);
                  $(this).parents("div.col-sm-2.text-center").siblings().find("input[type=checkbox]").attr("required","true")
            
            }

            if (return_qty >= delivered_qty){
                $(this).val(delivered_qty);
                $(this).parents("div.col-sm-2.text-center").siblings().find("input[type=checkbox]").prop("checked", true);
                $(this).parent().siblings().find("select").attr("required","true")
                $(this).parent().siblings().find("input[type=text]").attr("required","true")
            }
         
        });

      
        $("input#btnsubmit").mouseover(function(){
        	checkbox_validate()
        })
        
        //bread-crumb
        $(".rma_breadcrumb").parents().siblings().find(".o_portal_submenu").css("display","none");
        
    });
})
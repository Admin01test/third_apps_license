Changelog
=========
Version 14.0.1
-------------------------

- Initial Release

v14.0.2 (Date : 19th Mar 2021)
----------------------------
 [ADD] partially payment for pdc cheque
 [ADD] notification for cheque due date
 
 v14.0.3 (27/05/2021)
 
 -----------------------
  
Reconcile all receivable entries
In pdc.wizard model's tree view , sum of all payment amounts.
In pdc.wizard model Multi Action for all states.

v14.0.4(15th November , 2021)

1) PDC must only be allowed to be deleted only when the status is ‘draft’.
2) Reset to Draft in Action of pdc form. On click of this action only Done and Cancelled pdc will be reset to draft
3) PDC form will be editable in Returned state
4) Multiple invoices in pdc view, create pdc payment of multiple invoices (multi action in invoice)
5) add one field done date in pdc form view
6) Add chatter to pdc
7) When there is no invoice, it should not allow the user to register and give a warning message.
8) when click on view button of payment bank journal entry should be opened
9) in pdc form view if payment amount is greatar than amount residual raise error

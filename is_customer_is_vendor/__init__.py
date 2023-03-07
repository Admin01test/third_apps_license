from . import models


def update_old_partners(cr, registry):
    # Update Customer
    cr.execute("UPDATE res_partner SET customer='t' where customer_rank > 0;")
    # Update Supplier
    cr.execute("UPDATE res_partner SET supplier='t' where supplier_rank > 0;")

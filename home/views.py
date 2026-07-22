import profile
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
import requests

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models.functions import TruncMonth
from home.de import treasurer_required
from .forms import *
import csv
import datetime
from .service import SaccoReportService
from django.db.models import Q, Sum, Avg
from django.contrib import messages
from django.db.models import Sum
from django.contrib.admin.views.decorators import staff_member_required
from datetime import date, timedelta
from .deco import staff_required
from .models import Transaction, ActivityLog
from dateutil.relativedelta import relativedelta # Use 'pip install python-dateutil'
from django.http import HttpResponse
from .mpesa_utils import get_mpesa_access_token, get_mpesa_password
import requests
from django.utils import timezone
from django.db import  transaction
from decimal import Decimal, DecimalException
from decimal import Decimal, InvalidOperation
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.forms import modelformset_factory
from django.db.models import F
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .utils import generate_transaction_ref , calculate_insurance # Make sure you have a function to generate unique references
import json
from .pamision import role_required
from Users.models import CustomUser
import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from Users.utils import send_brevo_email
from decimal import Decimal
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.db import transaction
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
def devloper(request):
    return render(request, "devloper.html")
@login_required
def update_savings_goal(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_goal = Decimal(data.get('goal', 0))
            
            profile = request.user.profile
            profile.monthly_saving_target = new_goal
            profile.save()
            
            return JsonResponse({'status': 'success', 'new_goal': str(new_goal)})
        except (ValueError, Decimal.InvalidOperation):
            return JsonResponse({'status': 'error', 'message': 'Invalid amount'}, status=400)
    return JsonResponse({'status': 'error'}, status=405)
def home(request):
    total_members=Profile.objects.count()
    total_loans=Loan.objects.count()
    context={
        'total_members':total_members,
        'total_loans':total_loans
    }
    return render(request, "home.html",context)
def about(request):
    return render (request, "about.html")


from django.shortcuts import render
from django.contrib import messages
from django.template.loader import render_to_string

def Contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        # Context for the HTML email template
        context = {
            'name': name,
            'email': email,
            'phone': phone,
            'subject': subject,
            'message': message,
        }

        # Create the styled HTML body
        html_content = render_to_string('contact_email_template.html', context)

        try:
            send_brevo_email(
                to_email="kevinmalasa2000@gmail.com",
                subject=f"New Contact Inquiry: {subject}",
                html_content=html_content
            )
            messages.success(request, "Your message has been sent successfully! We will get back to you soon.")
        except Exception as e:
            messages.error(request, "There was an error sending your message. Please try again later.")
    
    return render(request, "contact.html")
def Service(request):
    return render (request,  "services.html")

# mpesa/views.py
import json
import logging
from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from .models import CapitalShare, MonthlyContribution, Loan, XmasLoan, LoanRepayment, Transaction, Profile
import logging
import json
from decimal import Decimal
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from .models import Transaction, Profile, CapitalShare, MonthlyContribution, XmasLoan, Loan, LoanRepayment
def tran(request):
    s= Transaction.objects.all()
    return render(request, "tans.html", {'s':s})
logger = logging.getLogger(__name__)
import json
import logging
from decimal import Decimal
from django.http import JsonResponse
from django.db import transaction
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .models import Profile, CapitalShare, MonthlyContribution, XmasLoan, Loan, LoanRepayment, Transaction

logger = logging.getLogger(__name__)
@csrf_exempt
@csrf_exempt
def mpesa_callback(request):
    try:
        raw_body = request.body.decode('utf-8')
        logger.info(f"🔵 RAW CALLBACK: {raw_body[:500]}...")
        
        data = json.loads(raw_body)
        callback = data.get('Body', {}).get('stkCallback', {})
        
        result_code = callback.get('ResultCode')
        result_desc = callback.get('ResultDesc')
        
        logger.info(f"🔵 ResultCode: {result_code}, ResultDesc: {result_desc}")
        
        if result_code != 0:
            logger.warning(f"⚠️ Transaction Failed: {result_desc}")
            return JsonResponse({"ResultCode": 0})

        # Extract metadata
        metadata_items = callback.get('CallbackMetadata', {}).get('Item', [])
        metadata = {}
        for item in metadata_items:
            metadata[item['Name']] = item.get('Value')
        
        logger.info(f"🔵 Metadata: {metadata}")
        
        amount = metadata.get('Amount')
        receipt = metadata.get('MpesaReceiptNumber')
        checkout_request_id = callback.get('CheckoutRequestID')
        phone = metadata.get('PhoneNumber')
        
        logger.info(f"🔵 Amount: {amount}, Receipt: {receipt}, CheckoutID: {checkout_request_id}, Phone: {phone}")

        if not receipt or not amount:
            logger.error("❌ Missing receipt or amount")
            return JsonResponse({"ResultCode": 0})
        
        amount_decimal = Decimal(str(amount))

        # Find pending transaction
        pending_txn = None
        
        # 1. Try by CheckoutRequestID
        if checkout_request_id:
            try:
                pending_txn = PendingMpesaTransaction.objects.get(
                    checkout_request_id=checkout_request_id,
                    processed=False
                )
                logger.info(f"✅ Found pending by CheckoutID: {pending_txn}")
            except PendingMpesaTransaction.DoesNotExist:
                logger.warning(f"⚠️ No pending by CheckoutID: {checkout_request_id}")
        
        # 2. If not found, try by phone number
        if not pending_txn and phone:
            try:
                phone_clean = phone
                if phone_clean.startswith('254'):
                    phone_clean = '0' + phone_clean[3:]
                
                pending_txn = PendingMpesaTransaction.objects.filter(
                    phone_number__icontains=phone_clean[-9:],
                    processed=False
                ).order_by('-created_at').first()
                
                if pending_txn:
                    logger.info(f"✅ Found pending by phone: {pending_txn}")
                    if checkout_request_id:
                        pending_txn.checkout_request_id = checkout_request_id
                        pending_txn.save()
            except Exception as e:
                logger.error(f"❌ Error finding by phone: {str(e)}")
        
        # 3. If still not found, try by amount (last resort)
        if not pending_txn:
            try:
                pending_txn = PendingMpesaTransaction.objects.filter(
                    amount=amount_decimal,
                    processed=False
                ).order_by('-created_at').first()
                if pending_txn:
                    logger.info(f"✅ Found pending by amount: {pending_txn}")
                    if checkout_request_id:
                        pending_txn.checkout_request_id = checkout_request_id
                        pending_txn.save()
            except Exception as e:
                logger.error(f"❌ Error finding by amount: {str(e)}")
        
        # Process the transaction
        if pending_txn:
            logger.info(f"🔵 Processing pending: {pending_txn}")
            
            target_member = pending_txn.member
            payment_type = pending_txn.payment_type
            loan_id = pending_txn.loan_id
            
            with transaction.atomic():
                target_member_obj = None
                t_type = ''
                success = False
                
                try:
                    if payment_type == 'shares':
                        logger.info("🔵 Processing SHARES")
                        CapitalShare.objects.create(
                            member=target_member, 
                            amount=amount_decimal,
                            month=timezone.now().date(),
                            date_created=timezone.now()
                        )
                        target_member_obj, t_type = target_member, 'shares'
                        success = True
                    
                    elif payment_type == 'savings':
                        logger.info("🔵 Processing SAVINGS")
                        MonthlyContribution.objects.create(
                            member=target_member, 
                            amount=int(amount_decimal),
                            month=timezone.now().date()
                        )
                        target_member_obj, t_type = target_member, 'savings'
                        success = True
                    
                    elif payment_type == 'bereavement':  # ✅ Corrected from 'Berevement'
                        logger.info("🔵 Processing BEREAVEMENT")
                        # Create payment record
                        BereavementPayment.objects.create(
                            member=target_member,
                            amount=amount_decimal,
                            payment_month=timezone.now().month,
                            payment_year=timezone.now().year,
                            status='paid',
                            reference=receipt,
                            notes=f"M-Pesa payment for {receipt}"
                        )
                        # Mark member as paid for all active announcements they haven't paid for yet
                        unpaid_anns = BereavementAnnouncement.objects.filter(
                            is_active=True,
                            is_approved=True
                        ).exclude(member=target_member).exclude(paid_by=target_member)
                        for ann in unpaid_anns:
                            ann.paid_by.add(target_member)
                        target_member_obj, t_type = target_member, 'bereavement'
                        success = True
                    
                    elif payment_type == 'xmas':
                        logger.info("🔵 Processing XMAS")
                        if not loan_id:
                            raise ValueError("Loan ID required")
                        loan = XmasLoan.objects.get(id=loan_id)
                        LoanRepayment.objects.create(
                            member=loan.member, 
                            amount_paid=amount_decimal,
                            reference=receipt,
                            is_xmas=True,
                            xmas_loan=loan
                        )
                        target_member_obj, t_type = loan.member, 'repayment'
                        success = True
                    
                    elif payment_type == 'loan':
                        logger.info("🔵 Processing LOAN")
                        if not loan_id:
                            raise ValueError("Loan ID required")
                        loan = Loan.objects.get(id=loan_id)
                        LoanRepayment.objects.create(
                            loan=loan,
                            member=loan.member, 
                            amount_paid=amount_decimal,
                            reference=receipt,
                            is_xmas=False
                        )
                        target_member_obj, t_type = loan.member, 'repayment'
                        success = True
                    
                    else:
                        logger.error(f"❌ Unknown type: {payment_type}")
                        return JsonResponse({"ResultCode": 0})
                    
                    # Create Transaction record
                    if success and target_member_obj:
                        Transaction.objects.create(
                            member=target_member_obj, 
                            transaction_type=t_type, 
                            amount=amount_decimal,
                            reference=receipt
                        )
                        logger.info(f"✅ Transaction created")
                        
                        # Mark pending as processed
                        pending_txn.processed = True
                        pending_txn.receipt_number = receipt
                        pending_txn.save()
                        logger.info(f"✅ Pending marked processed")
                    
                except Exception as e:
                    logger.error(f"❌ Error processing: {str(e)}")
                    import traceback
                    logger.error(f"❌ Traceback: {traceback.format_exc()}")
                    return JsonResponse({"ResultCode": 0})
            
            logger.info(f"✅ SUCCESS: {receipt}")
            return JsonResponse({"ResultCode": 0})
        
        else:
            logger.error("❌ No pending transaction found!")
            return JsonResponse({"ResultCode": 0})

    except Exception as e:
        logger.error(f"❌ Callback Error: {str(e)}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        return JsonResponse({"ResultCode": 1, "ErrorMessage": str(e)})
# def check_mpesa_status(request, transaction_id):
#     try:
#         sale = ProductSale.objects.get(id=transaction_id)
#         return JsonResponse({'payment_status': sale.payment_status})
#     except ProductSale.DoesNotExist:
#         return JsonResponse({'payment_status': 'NOT_FOUND'}, status=404)

@login_required
def approve_share_refund(request, refund_id):
    refund = get_object_or_404(CapitalShareRefund, id=refund_id)
    u_type = getattr(request.user, 'user_type', None)

    if refund.status in ['rejected', 'disbursed']:
        messages.error(request, "This share refund is already finalized.")
        return redirect('capital_share_refund_queue')

    # 1. Staff Approval
    if u_type == '2':
        refund.staff_approved = True
        refund.status = "staff_approved"
        messages.success(request, "Staff approval recorded for share refund.")

    # 2. Treasurer Approval
    elif u_type == '3':
        if not refund.staff_approved:
            messages.error(request, "Staff must approve this share refund first.")
        else:
            refund.treasurer_approved = True
            refund.status = "treasurer_approved"
            messages.success(request, "Treasurer approval recorded for share refund.")

    # 3. Admin Final Approval
    elif u_type == '1' or request.user.is_superuser:
        if not (refund.staff_approved and refund.treasurer_approved):
            messages.error(request, "Staff and Treasurer must approve first.")
        else:
            refund.admin_approved = True
            refund.status = "approved"
            messages.success(request, "Share refund fully approved. Ready for disbursement.")
    
    else:
        messages.error(request, "Unauthorized action.")

    refund.save()
    return redirect('capital_share_refund_queue')
@login_required
def reject_share_refund(request, refund_id):
    refund = get_object_or_404(CapitalShareRefund, id=refund_id)
    u_type = getattr(request.user, 'user_type', None)

    if u_type not in ['1', '2', '3'] and not request.user.is_superuser:
        messages.error(request, "Unauthorized.")
        return redirect('member_dashboard')

    if refund.status in ['disbursed', 'rejected']:
        messages.warning(request, "This refund is already finalized.")
    else:
        refund.status = 'rejected'
        refund.save()
        messages.success(request, f"Share refund for {refund.member.user.get_full_name()} has been rejected.")

    return redirect('capital_share_refund_queue')
@login_required

@transaction.atomic
def disburse_share_refund(request, refund_id):
    # =====================================================
    # 1. PERMISSION CHECK
    # =====================================================
    if getattr(request.user, 'user_type', None) != '3':
        messages.error(request, "Only the Treasurer can disburse share refunds.")
        return redirect('capital_share_refund_queue')
    
    refund = get_object_or_404(CapitalShareRefund, id=refund_id)

    # =====================================================
    # 2. VALIDATION CHECKS
    # =====================================================
    if not refund.admin_approved:
        messages.error(request, "Admin final sign-off is required before disbursement.")
        return redirect('capital_share_refund_queue')

    if refund.status == 'disbursed':
        messages.warning(request, "This refund has already been disbursed.")
        return redirect('capital_share_refund_queue')

    if refund.status == 'rejected':
        messages.error(request, "This refund has been rejected and cannot be disbursed.")
        return redirect('capital_share_refund_queue')

    member = refund.member
    user = member.user 

    try:
        # =====================================================
        # 3. CALCULATE OUTSTANDING LOANS (WELFARE: No interest)
        # =====================================================
        # WELFARE: Get all active loans (pending, approved, disbursed)
        active_loans = Loan.objects.filter(
            member=member, 
            status__in=['pending', 'approved', 'disbursed']
        )
        
        # Calculate total loan debt (principal only - no interest)
        total_loan_debt = Decimal('0.00')
        for loan in active_loans:
            total_loan_debt += loan.get_remaining_balance() or Decimal('0.00')
        
        # WELFARE: Also check Xmas loans
        active_xmas_loans = XmasLoan.objects.filter(
            member=member,
            status__in=['pending', 'approved', 'disbursed']
        )
        for xloan in active_xmas_loans:
            total_loan_debt += xloan.remaining_balance or Decimal('0.00')
        
        # =====================================================
        # 4. PROCESSING FEE (WELFARE: Reduced to KES 500)
        # =====================================================
        processing_fee = Decimal('1000.00')  # WELFARE: Reduced fee
        
        gross_shares = refund.amount_requested
        
        # =====================================================
        # 5. FINAL CALCULATION
        # =====================================================
        total_deductions = total_loan_debt + processing_fee
        final_payout = gross_shares - total_deductions

        if final_payout < 0:
            messages.error(
                request, 
                f"Cannot disburse. Member owes KES {abs(final_payout):,.2f} more than their shares. "
                f"Outstanding debt: KES {total_loan_debt:,.2f}"
            )
            return redirect('capital_share_refund_queue')

        # =====================================================
        # 6. UPDATE CAPITAL SHARE LEDGER
        # =====================================================
        CapitalShare.objects.create(
            member=member,
            amount=-(gross_shares),  # Negative amount to deduct shares
            date_created=timezone.now().date(),
        )

        # =====================================================
        # 7. UPDATE REFUND STATUS
        # =====================================================
        refund.status = 'disbursed'
        refund.net_amount = final_payout
        refund.date_disbursed = timezone.now()
        refund.save()

        # =====================================================
        # 8. LOG THE TRANSACTION
        # =====================================================
        Transaction.objects.create(
            member=member,
            transaction_type='shares',
            amount=-(gross_shares),
            reference=f"SHARE_REFUND_{refund.id}",
            created_at=timezone.now()
        )

        # =====================================================
        # 9. CONDITIONAL DELETE (Only if 'exit' reason)
        # =====================================================
        user_display_name = user.get_full_name() or user.username
        
        if refund.reason == 'exit':
            # Store name before deletion
            user.delete() 
            success_msg = f"Successfully disbursed exit refund and CLOSED account for {user_display_name}."
        else:
            success_msg = f"Successfully disbursed refund for {user_display_name}. Account remains active."

        messages.success(
            request, 
            f"{success_msg} Final Payout: KES {final_payout:,.2f} "
            f"(Deductions: KES {total_loan_debt:,.2f} loans, KES {processing_fee:,.2f} fee)."
        )

    except Exception as e:
        messages.error(request, f"Disbursement failed: {str(e)}")
        # Transaction will rollback automatically due to @transaction.atomic

    return redirect('capital_share_refund_queue')

def apply_xmas_refund(request):
    # Accessing the Profile through the OneToOne relationship
    profile = request.user.profile
    current_year = timezone.now().year
    
    # 1. Logic: Use monthly_saving_target from Profile
    monthly_target = profile.monthly_saving_target
    
    if monthly_target <= 0:
        messages.error(request, "Your monthly saving target is not set. Please update your profile.")
        return redirect('member_dashboard')

    # Calculate Annual Cap
    annual_target_cap = monthly_target * 12

    # 2. Get ACTUAL accumulated savings from the ledger
    # This ensures they don't withdraw money they haven't actually saved yet
    actual_savings = MonthlyContribution.objects.filter(
        member=profile
    ).aggregate(total=Sum('amount'))['total'] or 0

    # 3. Final Eligible Amount: Whichever is LOWER
    # They get their target X 12 OR what they actually have in the account
    total_eligible_amount = min(annual_target_cap, actual_savings)

    # 4. Double Check for existing application
    already_applied = XmasRefund.objects.filter(member=profile, year=current_year).exists()

    if request.method == 'POST':
        if already_applied:
            messages.warning(request, f"You have already applied for your {current_year} Xmas refund.")
        elif total_eligible_amount <= 0:
            messages.error(request, "Your eligible refund amount is 0 based on your current savings.")
        else:
            XmasRefund.objects.create(
                member=profile,
                amount_requested=total_eligible_amount,
                year=current_year,
                status='pending' # Explicitly setting initial status
            )
            messages.success(request, f"Xmas Refund request of KES {total_eligible_amount:,.2f} submitted successfully!")
        return redirect('member_dashboard')

    context = {
        'monthly_target': monthly_target,
        'annual_target_cap': annual_target_cap,
        'actual_savings': actual_savings,
        'total_eligible_amount': total_eligible_amount,
        'already_applied': already_applied,
        'current_year': current_year
    }
    return render(request, 'apply_xmas_refund.html', context)
@login_required
def cancel_share_refund(request, refund_id):
    refund = get_object_or_404(
        CapitalShareRefund,
        id=refund_id,
        member=request.user.profile
    )

    approvals_count = (
        int(refund.staff_approved) +
        int(refund.treasurer_approved) +
        int(refund.admin_approved)
    )

    if approvals_count >= 2:
        messages.error(
            request,
            "This refund cannot be cancelled because it has already received multiple approvals."
        )
        return redirect('member_dashboard')

    if refund.status in ['disbursed', 'rejected']:
        messages.error(
            request,
            "This refund cannot be cancelled."
        )
        return redirect('member_dashboard')

    refund.delete()

    messages.success(
        request,
        "Your share refund request has been cancelled successfully."
    )

    return redirect('member_dashboard')
def apply_share_refund(request):
    profile = request.user.profile
    current_year = timezone.now().year

    # prevent multiple active requests
    existing = CapitalShareRefund.objects.filter(
        member=profile,
        year=current_year,
        status__in=['pending', 'partially_approved', 'approved']
    ).first()

    if existing:
        messages.warning(request, "You already have a pending share refund request.")
        return redirect('member_dashboard')

    # total shares
    total_shares = CapitalShare.objects.filter(member=profile).aggregate(
        Sum('amount')
    )['amount__sum'] or Decimal('0.00')

    if total_shares <= 0:
        messages.error(request, "You have no capital shares to refund.")
        return redirect('member_dashboard')

    processing_fee_rate = Decimal('0.05')  # 5%

    if request.method == 'POST':
        amount = Decimal(request.POST.get('amount'))

        if amount > total_shares:
            messages.error(request, "You cannot refund more than your total shares.")
            return redirect('apply_share_refund')

        # CALCULATIONS
        processing_fee = 1000
        net_amount = amount - processing_fee

        effective_date = timezone.now() + timedelta(days=90)

        refund = CapitalShareRefund.objects.create(
            member=profile,
            amount_requested=amount,
            reason=request.POST.get('reasons'),
            
            net_amount=net_amount,
            effective_date=effective_date
        )

        # =========================
        # NOTIFICATIONS (MEMBER)
        # =========================
        messages.success(
            request,
            f"Your share refund request has been submitted successfully. "
            f"Net amount you will receive: KES {net_amount:,.2f}. "
            f"Processing fee applied: KES {processing_fee:,.2f}. "
            f"This refund will be effective after 3 months."
        )

       

        return redirect('member_dashboard')

    return render(request, 'apply_share_refund.html', {
        'total_shares': total_shares
    })



def capital_share_refund_queue(request):
    user = request.user
    u_type = getattr(user, 'user_type', None)

    # Allow only staff, treasurer, admin
    if u_type not in ['1', '2', '3']:
        messages.error(request, "Unauthorized access.")
        return redirect('member_dashboard')

    refunds = CapitalShareRefund.objects.select_related('member').order_by('-date_applied')
    
    # Calculate approval progress for each refund
    for refund in refunds:
        refund.approval_count = (
            int(refund.staff_approved) + 
            int(refund.treasurer_approved) + 
            int(refund.admin_approved)
        )
        
        # Determine current stage
        if refund.status == 'disbursed':
            refund.current_stage = 'Disbursed'
        elif refund.status == 'approved':
            refund.current_stage = 'Fully Approved'
        elif refund.admin_approved:
            refund.current_stage = 'Admin Approved'
        elif refund.treasurer_approved:
            refund.current_stage = 'Treasurer Approved'
        elif refund.staff_approved:
            refund.current_stage = 'Staff Approved'
        else:
            refund.current_stage = 'Pending'

    return render(request, 'capital_share_refund_queue.html', {
        'refunds': refunds,
        'user_type': u_type,
    })
@login_required
def manage_refunds_list(request):
    refunds = XmasRefund.objects.all().order_by('-date_applied')
    user_role = request.user.user_type
    
    # Calculate approval progress for each refund
    for refund in refunds:
        refund.approval_progress = int(refund.staff_approved) + int(refund.treasurer_approved) + int(refund.admin_approved)
        
        # Determine current stage
        if refund.status == 'disbursed':
            refund.current_stage = 'Disbursed'
        elif refund.status == 'approved':
            refund.current_stage = 'Fully Approved'
        elif refund.admin_approved:
            refund.current_stage = 'Admin Approved'
        elif refund.treasurer_approved:
            refund.current_stage = 'Treasurer Approved'
        elif refund.staff_approved:
            refund.current_stage = 'Staff Approved'
        else:
            refund.current_stage = 'Pending'
    
    context = {
        'refunds': refunds,
        'user_role': user_role,
    }
    return render(request, 'admin_refund_list.html', context)


def disburse_xmas_refund(request, refund_id):
    if request.user.user_type != '3':  # Treasurer Check
        messages.error(request, "Only the Treasurer can disburse funds.")
        return redirect('manage_refunds_list')

    refund = get_object_or_404(XmasRefund, id=refund_id)

    if not refund.admin_approved:
        messages.error(request, "Admin approval required before disbursement.")
        return redirect('manage_refunds_list')

    if refund.status == 'disbursed':
        messages.warning(request, "This refund has already been processed.")
        return redirect('manage_refunds_list')

    try:
        with transaction.atomic():
            refund.status = 'disbursed'
            refund.date_disbursed = timezone.now()
            refund.save()

            MonthlyContribution.objects.create(
                member=refund.member,
                amount=-(refund.amount_requested),
                month=timezone.now().date(),
            )

            messages.success(request, f"KES {refund.amount_requested:,.2f} disbursed and savings updated.")
            
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")

    return redirect('manage_refunds_list')
@login_required
def approve_xmas_refund(request, refund_id):
    refund = get_object_or_404(XmasRefund, id=refund_id)
    user = request.user
    u_type = getattr(user, 'user_type', None)

    # ❌ Prevent modifying finalized refunds
    if refund.status in ['rejected', 'disbursed']:
        messages.error(request, "This refund is already finalized.")
        return redirect('manage_refunds_list')

    # ---------------------------------------------------------
    # 1️⃣ STAFF APPROVAL
    # ---------------------------------------------------------
    if u_type == '2':
        if refund.staff_approved:
            messages.info(request, "Already approved by staff.")
            return redirect('manage_refunds_list')

        refund.staff_approved = True
        refund.status = "partially_approved"
        refund.save()

        messages.success(request, "Staff approval recorded.")
        return redirect('manage_refunds_list')

    # ---------------------------------------------------------
    # 2️⃣ TREASURER APPROVAL
    # ---------------------------------------------------------
    elif u_type == '3':
        if not refund.staff_approved:
            messages.error(request, "Staff must approve first.")
            return redirect('manage_refunds_list')

        if refund.treasurer_approved:
            messages.info(request, "Already approved by Treasurer.")
            return redirect('manage_refunds_list')

        refund.treasurer_approved = True
        refund.status = "partially_approved"
        refund.save()

        messages.success(request, "Treasurer approval recorded.")
        return redirect('manage_refunds_list')

    # ---------------------------------------------------------
    # 3️⃣ ADMIN FINAL APPROVAL
    # ---------------------------------------------------------
    elif u_type == '1' or user.is_superuser:
        if not (refund.staff_approved and refund.treasurer_approved):
            messages.error(request, "Staff and Treasurer must approve first.")
            return redirect('manage_refunds_list')

        if refund.admin_approved:
            messages.info(request, "Already approved by Admin.")
            return redirect('manage_refunds_list')

        refund.admin_approved = True
        refund.status = "approved"
        refund.save()

        messages.success(request, "Refund fully approved. Ready for disbursement.")
        return redirect('manage_refunds_list')

    else:
        messages.error(request, "Unauthorized action.")
        return redirect('manage_refunds_list')
# def manage_refunds_list(request):
#     refunds = XmasRefund.objects.all().order_by('-date_applied')
#     # Passing the role string ('1', '2', etc.) to the template
#     user_role = request.user.user_type
    
#     context = {
#         'refunds': refunds,
#         'user_role': user_role,
#     }
#     return render(request, 'admin_refund_list.html', context)
def reject_xmas_refund(request, refund_id):
    refund = get_object_or_404(XmasRefund, id=refund_id)
    user = request.user
    u_type = getattr(user, 'user_type', None)

    # Only staff/treasurer/admin can reject
    if u_type not in ['1', '2', '3'] and not user.is_superuser:
        messages.error(request, "You are not allowed to reject this refund.")
        return redirect('member_dashboard')

    # Prevent rejecting finalized
    if refund.status in ['disbursed', 'rejected']:
        messages.warning(request, "This refund is already finalized.")
        return redirect('staff_dashboard')

    refund.status = 'rejected'
    refund.save()

    messages.success(request, "Refund has been rejected.")
    return redirect('staff_dashboard')
def apply_xmas_loan(request):
    profile = request.user.profile

    # =====================================================
    # WELFARE: TOTAL SHARE-BASED LIMIT
    # =====================================================
    total_shares = MonthlyContribution.objects.filter(member=profile).aggregate(
        Sum('amount')
    )['amount__sum'] or Decimal('0.00')

    # WELFARE: Max limit is 3.5x of total shares
    total_limit = total_shares 
    

    # =====================================================
    # CURRENT ACTIVE LOANS (TOP-UP LOGIC)
    # =====================================================
    active_loans = XmasLoan.objects.filter(
        member=profile
    ).exclude(status__in=['rejected', 'cleared'])

    # Calculate total borrowed using remaining balance
    total_borrowed = sum(loan.remaining_balance for loan in active_loans)

    # =====================================================
    # AVAILABLE LIMIT
    # =====================================================
    available_limit = total_limit - total_borrowed

    if available_limit <= 0:
        messages.error(
            request,
            "You have reached your loan limit. Clear your existing loan to borrow again."
        )
        return redirect('member_dashboard')

    # =====================================================
    # HANDLE FORM SUBMISSION
    # =====================================================
    if request.method == 'POST':

        amount_input = request.POST.get('amount', '').strip()
        duration_input = request.POST.get('duration', '').strip()

        if not amount_input:
            messages.error(request, "Please enter an amount.")
            return redirect(request.path)

        if not duration_input:
            messages.error(request, "Please select a repayment period.")
            return redirect(request.path)

        try:
            amount = Decimal(str(amount_input))
            duration = int(duration_input)
        except (InvalidOperation, ValueError):
            messages.error(request, "Enter valid numeric values.")
            return redirect(request.path)

        # =====================================================
        # VALIDATIONS
        # =====================================================
        if amount <= 0:
            messages.error(request, "Amount must be greater than zero.")

        elif duration < 1 or duration > 12:
            messages.error(request, "Repayment period must be between 1 and 12 months.")

        elif amount > available_limit:
            messages.error(
                request,
                f"Limit exceeded! You can only borrow up to KES {available_limit:,.2f}"
            )

        else:
            # =====================================================
            # WELFARE: CALCULATE INTEREST (20% of principal)
            # =====================================================
            interest_rate = Decimal('20.00')  # 20%
            interest_amount = amount * (interest_rate / Decimal('100'))
            
            # Total payable = Principal + Interest
            total_payable = amount + interest_amount
            
            # Monthly installment = Total payable / duration
            monthly_installment = total_payable / Decimal(duration)

            # =====================================================
            # CREATE LOAN
            # =====================================================
            with transaction.atomic():
                loan = XmasLoan.objects.create(
                    member=profile,
                    amount_requested=amount,
                    interest_rate=interest_rate,  # 20%
                    installments=duration,
                    repayment_period=duration
                )
                
                # =====================================================
                # CREATE REPAYMENT SCHEDULE
                # =====================================================
                from dateutil.relativedelta import relativedelta
                from datetime import date
                
                start_date = date.today()
                
                for i in range(1, duration + 1):
                    due_date = start_date + relativedelta(months=i)
                    
                    LoanRepaymentSchedule.objects.create(
                        xmas_loan=loan,
                        is_xmas=True,
                        installment_number=i,
                        due_date=due_date,
                        # amount_due=amount / Decimal(duration),
                        amount_due=monthly_installment,
                        is_paid=False
                    )

            messages.success(
                request,
                f"Loan applied successfully! "
                f"Principal: KES {amount:,.2f} | "
                f"Interest (20%): KES {interest_amount:,.2f} | "
                f"Total: KES {total_payable:,.2f} | "
                f"Duration: {duration} months"
            )
            return redirect('member_dashboard')

    # =====================================================
    # RENDER PAGE
    # =====================================================
    return render(request, 'xmas.html', {
        'max_limit': available_limit,
        'total_limit': total_limit,
        'borrowed': total_borrowed,
        'interest_rate': 20,  # 20% interest
    })
    
def pay_xmas_loan(request):
    current_year = timezone.now().year

    loan = XmasLoan.objects.filter(
        member=request.user.profile,
        # year=current_year,
        status='disbursed'
    ).first()

    if not loan:
        messages.error(request, "You do not have an active disbursed Xmas Loan for this year.")
        return redirect('member_dashboard')

    # Suggested installment logic
    suggested_installment = min(loan.monthly_installment, loan.remaining_balance)

    # Remaining months calculation
    remaining_months = 0
    if loan.monthly_installment > 0:
        remaining_months = int((loan.remaining_balance / loan.monthly_installment).quantize(Decimal('1')))

    if request.method == 'POST':
        amount_input = request.POST.get('amount')
        try:
            amount_to_pay = Decimal(amount_input)
            if amount_to_pay <= 0:
                raise ValueError
        except (ValueError, TypeError, InvalidOperation):
            messages.error(request, "Please enter a valid numerical amount.")
            return redirect('pay_xmas_loan')

        # Trigger M-Pesa instead of saving to DB
        # We redirect to the initiate_stk_push view or call its logic directly
        return initiate_stk_push(request) 

    return render(request, 'pay_loanx.html', {
        'loan': loan,
        'suggested_installment': suggested_installment,
        'remaining_months': remaining_months
    })
@login_required
@role_required(allowed_roles=['1', '2', '3', '4'])  # Allow all roles to access dashboard



def update_targetds(request):
    if request.method == "POST":
        profile = request.user.profile
        data = json.loads(request.body)

        share_goal = data.get('share_goal')
        saving_target = data.get('saving_target')

        if share_goal:
            profile.share_goal = share_goal

        if saving_target:
            profile.monthly_saving_target = saving_target

        profile.save()

        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'failed'})
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from decimal import Decimal
from datetime import date
from .models import (
    Profile, Loan, XmasLoan, MonthlyContribution, CapitalShare,
    BereavementAnnouncement, BereavementPayment,
    CapitalShareRefund, XmasRefund, LoanRepayment,
    RetirementAnnouncement, RetirementPayment  # new models
)
@login_required
def member_dashboard(request):
    profile = request.user.profile
    today = date.today()
    current_month = today.month
    current_year = today.year

    # ---- Loans ----
    loans = Loan.objects.filter(member=profile).order_by('-application_date')
    xmas_loans = XmasLoan.objects.filter(member=profile).order_by('-application_date')
    savings_list = MonthlyContribution.objects.filter(member=profile).order_by('-month', '-created_at')
    shares_list = CapitalShare.objects.filter(member=profile)
    bereavement_requests = BereavementPayment.objects.filter(member=profile)

    # ---- Bereavement announcements (simplified) ----
    active_bereavements = []
    all_anns = BereavementAnnouncement.objects.filter(
        is_active=True,
        is_approved=True
    ).order_by('-created_at')

    for ann in all_anns:
        is_owner = (ann.member == profile)
        total_instalments = ann.repayment_months
        paid_instalments = BereavementPayment.objects.filter(
            member=profile,
            announcement=ann,
            status='paid'
        ).count()
        fully_paid = (paid_instalments >= total_instalments)

        # Always show if not fully paid, or if the user is the owner
        if not fully_paid or is_owner:
            paid_this_month = BereavementPayment.objects.filter(
                member=profile,
                announcement=ann,
                payment_month=current_month,
                payment_year=current_year,
                status='paid'
            ).exists()

            active_bereavements.append({
                'announcement': ann,
                'mourner': ann.member,
                'deceased_name': ann.deceased_name,
                'relationship': ann.get_relationship_display(),
                'monthly_amount': ann.monthly_amount_per_member,
                'is_owner': is_owner,
                'fully_paid': fully_paid,
                'paid_this_month': paid_this_month,
            })

    # ---- Retirement announcements (simplified) ----
    active_retirements = []
    all_ret_anns = RetirementAnnouncement.objects.filter(
        is_active=True,
        is_approved=True
    ).order_by('-created_at')

    for ann in all_ret_anns:
        is_owner = (ann.member == profile)
        total_instalments = ann.repayment_months
        paid_instalments = RetirementPayment.objects.filter(
            member=profile,
            announcement=ann,
            status='paid'
        ).count()
        fully_paid = (paid_instalments >= total_instalments)

        if not fully_paid or is_owner:
            paid_this_month = RetirementPayment.objects.filter(
                member=profile,
                announcement=ann,
                payment_month=current_month,
                payment_year=current_year,
                status='paid'
            ).exists()

            active_retirements.append({
                'announcement': ann,
                'retiree': ann.member,
                'retirement_date': ann.retirement_date,
                'monthly_amount': ann.monthly_amount_per_member,
                'is_owner': is_owner,
                'fully_paid': fully_paid,
                'paid_this_month': paid_this_month,
            })

    # ---- Share refunds (unchanged) ----
    active_refunds = CapitalShareRefund.objects.filter(
        member=profile,
        status__in=['pending', 'staff_approved', 'treasurer_approved', 'approved']
    ).order_by('-date_applied')

    for refund in active_refunds:
        refund.approvals_count = (
            int(refund.staff_approved) +
            int(refund.treasurer_approved) +
            int(refund.admin_approved)
        )
        refund.progress_percent = (refund.approvals_count / 3) * 100
        if refund.admin_approved:
            refund.current_stage = "Fully Approved"
        elif refund.treasurer_approved:
            refund.current_stage = "Waiting for Admin Approval"
        elif refund.staff_approved:
            refund.current_stage = "Waiting for Treasurer Approval"
        else:
            refund.current_stage = "Waiting for Staff Approval"
        refund.can_cancel = refund.approvals_count < 2

    # ---- Xmas refunds (unchanged) ----
    xmas_refunds = XmasRefund.objects.filter(member=profile).order_by('-date_applied')
    for refund in xmas_refunds:
        refund.approvals_count = (
            int(refund.staff_approved) +
            int(refund.treasurer_approved) +
            int(refund.admin_approved)
        )
        refund.progress_percent = (refund.approvals_count / 3) * 100
        if refund.status == 'disbursed':
            refund.current_stage = "Disbursed ✅"
        elif refund.admin_approved:
            refund.current_stage = "Fully Approved"
        elif refund.treasurer_approved:
            refund.current_stage = "Waiting for Admin Approval"
        elif refund.staff_approved:
            refund.current_stage = "Waiting for Treasurer Approval"
        else:
            refund.current_stage = "Waiting for Staff Approval"
        refund.can_cancel = refund.approvals_count < 2 and refund.status != 'disbursed'

    # ---- Active loan counts ----
    active_normal_count = loans.filter(status__in=['pending', 'approved', 'disbursed']).count()
    active_xmas_count = xmas_loans.filter(status__in=['pending', 'approved', 'disbursed']).count()

    # ---- Loan calculations ----
    running_total_remaining_balance = Decimal('0.00')
    total_penalties = Decimal('0.00')

    for loan in loans:
        total_paid = LoanRepayment.objects.filter(loan=loan).aggregate(total=Sum('amount_paid'))['total'] or Decimal('0.00')
        loan.total_paid = total_paid
        loan.remaining_balance = max(loan.amount - total_paid, Decimal('0.00'))
        if loan.status in ['approved', 'disbursed']:
            running_total_remaining_balance += loan.remaining_balance

    # ---- Xmas loans ----
    for xmas in xmas_loans:
        if xmas.status in ['approved', 'disbursed']:
            if xmas.remaining_balance == 0 and xmas.status != 'cleared':
                xmas.status = 'cleared'
                xmas.save(update_fields=['status'])

    # ---- Savings ----
    current_month_savings = MonthlyContribution.objects.filter(
        member=profile,
        month__month=current_month,
        month__year=current_year
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    saving_target = getattr(profile, 'monthly_saving_target', Decimal('0.00'))
    savings_progress_pct = (current_month_savings / saving_target * 100) if saving_target else 0

    total_shares = shares_list.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    total_beravement = bereavement_requests.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    total_savings = savings_list.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    share_goal = getattr(profile, 'share_goal', Decimal('0.00'))
    share_progress_pct = (total_shares / share_goal * 100) if share_goal else 0
    share_progress_pct_capped = min(float(share_progress_pct), 100)
    circumference = 339.29
    dash_offset = circumference - ((share_progress_pct_capped / 100) * circumference)

    context = {
        'profile': profile,
        'loans': loans,
        'xmas_loans': xmas_loans,
        'active_normal_count': active_normal_count,
        'active_xmas_count': active_xmas_count,
        'savings': savings_list,
        'shares': shares_list,
        'active_refunds': active_refunds,
        'xmas_refunds': xmas_refunds,
        'total_savings': total_savings,
        'total_shares': total_shares,
        'total_loans': running_total_remaining_balance,
        'total_penalties': total_penalties,
        'total_beravement': total_beravement,
        'current_month_savings': current_month_savings,
        'saving_target': saving_target,
        'progress_pct': min(float(savings_progress_pct), 100),
        'share_goal': share_goal,
        'share_progress_pct': share_progress_pct_capped,
        'dash_offset': dash_offset,
        'active_bereavements': active_bereavements,
        'active_retirements': active_retirements,
    }

    return render(request, 'r_dashboard.html', context)
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Loan, XmasLoan, LoanRepaymentSchedule, Guarantor
from decimal import Decimal

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from .models import Loan, XmasLoan, LoanRepayment, Guarantor, LoanRepaymentSchedule

@login_required
def loan_details_json(request, loan_id, loan_type):
    profile = request.user.profile

    if loan_type == 'normal':
        try:
            loan = Loan.objects.get(id=loan_id, member=profile)
        except Loan.DoesNotExist:
            return JsonResponse({'error': 'Loan not found'}, status=404)

        schedules = LoanRepaymentSchedule.objects.filter(loan=loan, is_xmas=False).order_by('due_date')
        guarantors = Guarantor.objects.filter(loan=loan)

        # Total paid from repayments
        total_paid = loan.total_paid if hasattr(loan, 'total_paid') else Decimal('0.00')
        # Use the model's property if available
        remaining = loan.get_remaining_balance()
        # Get repayment records (not just schedule)
        repayments = LoanRepayment.objects.filter(loan=loan).order_by('-payment_date')

        data = {
            'id': loan.id,
            'purpose': loan.get_purpose_display(),   # human readable
            'amount': float(loan.amount),
            'interest_rate': float(loan.interest_rate),
            'interest': float(loan.interest or 0),
            'insurance': float(loan.insurance or 0),
            'total_payable': float(loan.total_payable),
            'duration_months': loan.duration_months,
            'monthly_installment': float(loan.monthly_installment),
            'total_paid': float(total_paid),
            'remaining_balance': float(remaining),
            'application_date': loan.application_date.strftime('%d %b %Y %H:%M'),
            'approval_date': loan.approval_date.strftime('%d %b %Y %H:%M') if loan.approval_date else None,
            'disbursed_at': loan.disbursed_at.strftime('%d %b %Y %H:%M') if loan.disbursed_at else None,
            'status': loan.status,
            'status_display': loan.get_status_display(),
            'is_legacy': loan.is_legacy,
            'legacy_balance': float(loan.legacy_balance) if loan.legacy_balance else 0,
            'guarantors': [
                {
                    'name': g.guarantor.user.get_full_name() or g.guarantor.user.username,
                    'amount': float(g.guaranteed_amount),
                    'status': g.status
                } for g in guarantors
            ],
            'schedules': [
                {
                    'installment': s.installment_number,
                    'due_date': s.due_date.strftime('%d %b %Y'),
                    'amount_due': float(s.amount_due),
                    'is_paid': s.is_paid,
                    'date_paid': s.date_paid.strftime('%d %b %Y') if s.date_paid else None
                } for s in schedules
            ],
            'repayments': [
                {
                    'amount': float(r.amount_paid),
                    'date': r.payment_date.strftime('%d %b %Y %H:%M'),
                    'reference': r.reference or 'N/A'
                } for r in repayments[:10]   # last 10 payments
            ],
        }
        return JsonResponse(data)

    elif loan_type == 'xmas':
        try:
            loan = XmasLoan.objects.get(id=loan_id, member=profile)
        except XmasLoan.DoesNotExist:
            return JsonResponse({'error': 'Loan not found'}, status=404)

        schedules = LoanRepaymentSchedule.objects.filter(xmas_loan=loan, is_xmas=True).order_by('due_date')
        repayments = LoanRepayment.objects.filter(xmas_loan=loan).order_by('-payment_date')

        data = {
            'id': loan.id,
            'amount_requested': float(loan.amount_requested),
            'interest_rate': float(loan.interest_rate),
            'total_interest': float(loan.total_interest),
            'total_payable': float(loan.total_payable),
            'installments': loan.installments,
            'monthly_installment': float(loan.monthly_installment),
            'total_paid': float(loan.total_paid),
            'remaining_balance': float(loan.remaining_balance),
            'application_date': loan.application_date.strftime('%d %b %Y %H:%M'),
            'approval_date': loan.approval_date.strftime('%d %b %Y %H:%M') if loan.approval_date else None,
            'disbursement_date': loan.disbursement_date.strftime('%d %b %Y %H:%M') if loan.disbursement_date else None,
            'status': loan.status,
            'status_display': loan.get_status_display(),
            'is_legacy': loan.is_legacy,
            'manual_interest': float(loan.manual_interest_amount) if loan.manual_interest_amount else None,
            'schedules': [
                {
                    'installment': s.installment_number,
                    'due_date': s.due_date.strftime('%d %b %Y'),
                    'amount_due': float(s.amount_due),
                    'is_paid': s.is_paid,
                    'date_paid': s.date_paid.strftime('%d %b %Y') if s.date_paid else None
                } for s in schedules
            ],
            'repayments': [
                {
                    'amount': float(r.amount_paid),
                    'date': r.payment_date.strftime('%d %b %Y %H:%M'),
                    'reference': r.reference or 'N/A'
                } for r in repayments[:10]
            ],
        }
        return JsonResponse(data)

    return JsonResponse({'error': 'Invalid loan type'}, status=400)
# def respond_guarantor(request, guarantor_id, action):
#     guarantor_req = get_object_or_404(
#         Guarantor.objects.select_related('loan'),
#         id=guarantor_id,
#         guarantor=request.user.profile
#     )

#     loan = guarantor_req.loan

#     # Prevent responding twice
#     if guarantor_req.status != 'pending':
#         messages.warning(request, "You have already responded to this request.")
#         return redirect('member_dashboard')

#     # Guard: loan must still be in guarantor stage
#     if loan.status != 'pending_guarantors':
#         messages.error(request, "This loan is no longer awaiting guarantor responses.")
#         return redirect('member_dashboard')

#     with transaction.atomic():
#         if action == 'accept':
#             guarantor_req.status = 'accepted'
#             guarantor_req.save(update_fields=['status'])

#             accepted_count = Guarantor.objects.filter(
#                 loan=loan,
#                 status='accepted'
#             ).count()

#             if accepted_count >= 3:
#                 loan.status = 'pending'  # moves to staff review
#                 loan.remarks = (
#                     f"All 3 guarantors approved. "
#                     f"Loan for {loan.member.user.get_full_name()} is now pending staff approval."
#                 )
#                 loan.save(update_fields=['status', 'remarks'])

#                 messages.success(request, "Final guarantor approval recorded.")
#             else:
#                 remaining = 3 - accepted_count
#                 messages.info(request, f"Response recorded. Waiting for {remaining} more guarantor(s).")

#         elif action == 'reject':
#             guarantor_req.status = 'rejected'
#             guarantor_req.save(update_fields=['status'])

#             loan.status = 'rejected'
#             loan.remarks = (
#                 f"Loan cancelled: Rejected by guarantor {request.user.get_full_name()}."
#             )
#             loan.save(update_fields=['status', 'remarks'])

#             messages.warning(request, "You declined the request. The application has been cancelled.")

#     return redirect('member_dashboard')

# # Ensure you import your STK helper: from .utils import initiate_stk_push

@login_required
def respond_guarantor(request, guarantor_id, action):
    guarantor = get_object_or_404(Guarantor, id=guarantor_id)
    loan = guarantor.loan

    if guarantor.guarantor != request.user.profile:
        messages.error(request, "Not your guarantor request.")
        return redirect('member_dashboard')

    if guarantor.status != 'pending':
        messages.error(request, "Already responded.")
        return redirect('member_dashboard')

    if action == 'accept':
        guarantor.status = 'accepted'
    else:
        guarantor.status = 'rejected'

    guarantor.save()

    # =====================================================
    # 🔥 CHECK IF ALL GUARANTORS ARE DONE
    # =====================================================
    remaining = Guarantor.objects.filter(
        loan=loan,
        status='pending'
    ).count()

    rejected = Guarantor.objects.filter(
        loan=loan,
        status='rejected'
    ).exists()

    if rejected:
        loan.status = 'rejected'
        loan.save()
        messages.error(request, "Loan rejected by guarantor.")
        return redirect('member_dashboard')

    # ✅ ALL GUARANTORS DONE → MOVE TO STAFF
    if remaining == 0:
        loan.status = 'pending'   # 👉 STAFF stage starts here
        loan.save()

    messages.success(request, "Response recorded.")
    return redirect('member_dashboard')
def treasurer_deposit_savings(request, member_id):
    member_profile = get_object_or_404(Profile, id=member_id)

    if request.method == "POST":
        form = SavingsForm(request.POST)
        payment_method = request.POST.get('payment_method')

        if form.is_valid():
            # Extract cleaned data
            amount = form.cleaned_data['amount']
            contribution_date = form.cleaned_data['month']

            if payment_method == 'mpesa':
                # Prep for STK Push
                request.POST = request.POST.copy()
                request.POST['payment_type'] = 'savings'
                request.POST['member_id'] = member_profile.id
                # Pass amount to the STK function if needed
                return initiate_stk_push(request)
            
            else:
                try:
                    with transaction.atomic():
                        # Save the MonthlyContribution record
                        saving = form.save(commit=False)
                        saving.member = member_profile
                        saving.save()

                        # Create the corresponding Transaction log
                        Transaction.objects.create(
                            member=member_profile,
                            transaction_type='deposit',
                            amount=amount,
                            reference=f"CASH-{request.POST.get('receipt_no', 'MANUAL')}"
                        )

                    messages.success(request, f"Cash deposit of KES {amount} for {contribution_date} recorded.")
                    return redirect('Members')
                except Exception as e:
                    messages.error(request, f"Database Error: {str(e)}")
        else:
            # This will show you exactly why validation failed in your console
            print(form.errors) 
            messages.error(request, "Invalid data. Please ensure the amount and month are correct.")
            
    else:
        form = SavingsForm()

    return render(request, 'treasurer_confirm_depost.html', {
        'member': member_profile, 
        'form': form
    })
@login_required
@login_required
def pay_bereavement_mpesa(request, announcement_id=None):
    profile = request.user.profile
    today = timezone.now().date()
    current_month = today.month
    current_year = today.year

    # --- Get active announcements (exclude own) ---
    active_anns = BereavementAnnouncement.objects.filter(
        is_active=True,
        is_approved=True
    ).exclude(member=profile)

    # If a specific announcement ID is provided, filter to that one
    if announcement_id:
        active_anns = active_anns.filter(id=announcement_id)
        if not active_anns.exists():
            messages.error(request, "Announcement not found or you are not eligible to pay it.")
            return redirect('member_dashboard')

    # Compute monthly due for this member
    monthly_due = Decimal('0.00')
    unpaid_announcements = []

    for ann in active_anns:
        # Check if this month falls within the repayment period
        end_month = ann.start_month + ann.repayment_months - 1
        end_year = ann.start_year
        while end_month > 12:
            end_month -= 12
            end_year += 1

        in_period = (
            (ann.start_year < current_year) or
            (ann.start_year == current_year and ann.start_month <= current_month)
        ) and (
            (end_year > current_year) or
            (end_year == current_year and end_month >= current_month)
        )

        if in_period:
            # Check if member has already paid this month's instalment
            payment_exists = BereavementPayment.objects.filter(
                member=profile,
                announcement=ann,
                payment_month=current_month,
                payment_year=current_year,
                status='paid'
            ).exists()
            if not payment_exists:
                monthly_due += ann.monthly_amount_per_member
                unpaid_announcements.append(ann)

    if monthly_due == 0:
        messages.info(request, "You have no pending bereavement contributions for this month.")
        return redirect('member_dashboard')

    # --- POST (process payment) ---
    if request.method == 'POST':
        phone = request.POST.get('phone')
        if not phone or len(phone) < 10:
            messages.error(request, "Please enter a valid phone number.")
            context = {
                'monthly_due': monthly_due,
                'announcements': unpaid_announcements,
                'month': today.strftime('%B %Y'),
                'phone_number': profile.phone_number or '',
            }
            return render(request, 'pay_bereavement_mpesa.html', context)

        # Create a pending payment record
        payment = BereavementPayment.objects.create(
            member=profile,
            amount=monthly_due,
            payment_month=current_month,
            payment_year=current_year,
            status='pending',
            reference=f"BEREAVE-{timezone.now().strftime('%Y%m%d%H%M%S')}",
            notes=f"Monthly payment covering {len(unpaid_announcements)} announcement(s)"
        )

        # Initiate STK Push
        request.POST = request.POST.copy()
        request.POST['payment_id'] = payment.id
        request.POST['payment_type'] = 'bereavement'
        request.POST['amount'] = str(monthly_due)
        request.POST['phone'] = phone

        return initiate_stk_push(request)

    # --- GET – show payment page ---
    context = {
        'monthly_due': monthly_due,
        'announcements': unpaid_announcements,
        'month': today.strftime('%B %Y'),
        'phone_number': profile.phone_number or '',
    }
    return render(request, 'pay_bereavement_mpesa.html', context)
  
def deposit_savings(request):
    """Member-only view: Strictly M-Pesa"""
    if request.method == "POST":
        form = SavingsForm(request.POST)
        if form.is_valid():
            # Inject payment_type so initiate_stk_push knows what to do
            request.POST = request.POST.copy()
            request.POST['payment_type'] = 'savings'
            # (member_id is not needed here as initiate_stk_push defaults to request.user.profile)
            
            return initiate_stk_push(request)
    else:
        form = SavingsForm()
        
    return render(request, "deposit_savings.html", {"form": form})
@login_required

def admin_dashboard(request):
    # if getattr(request.user, 'user_type', None) != '1' and not request.user.is_superuser:
    #     return redirect('access_denied')
    if not request.user.is_authenticated:
        return redirect('login')  # redundant with @login_required but safe

    if request.user.user_type != '1' and not request.user.is_superuser:
        
        return redirect('access_denied')
    pending_loans = Loan.objects.filter(
        status__in=['pending', 'partially_approved']
    )
    pending_xmas_loans = XmasLoan.objects.filter(
        status__in=['pending', 'partially_approved']
    ).order_by('-application_date')
    pending_xmas_refunds = XmasRefund.objects.filter(
        status__in=['pending', 'partially_approved']
    )
    approved_loans = Loan.objects.filter(status='approved')
    rejected_loans = Loan.objects.filter(status='rejected')
    pending_shares_refunds = CapitalShareRefund.objects.filter(
        status__in = ['staff_approved', 'treasurer_approved'],
        admin_approved=False
    ).order_by('-date_applied')
    all_members = Profile.objects.all() 

    total_savings_pool = MonthlyContribution.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    total_members = Profile.objects.count()
    total_interest_earned = Loan.objects.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or 0

    context = {
        'pending_xmas_loans': pending_xmas_loans,
        'pending_loans': pending_loans,
        'total_savings_pool': total_savings_pool,
        'total_members': total_members,
        'total_interest_earned': total_interest_earned,
        'approved_loans': approved_loans,
        'rejected_loans': rejected_loans,
        'all_members': all_members,
        'pending_shares_refunds': pending_shares_refunds,
        'pending_xmas_refunds': pending_xmas_refunds,
    }
    return render(request, 'rev.html', context)


def calculate_loan_risk(member_profile, requested_amount):
    total_active_loans = Loan.objects.filter(
        member=member_profile, 
        status__in=['pending','approved']
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    total_savings = CapitalShare.objects.filter(member=member_profile).aggregate(Sum('amount'))['amount__sum'] or 0

    risk_score = Decimal(requested_amount) / (Decimal(total_savings) + 1) + Decimal(total_active_loans) * Decimal('0.5')
    # Lower score = lower risk
    return risk_score
@login_required
@login_required
def apply_loan(request):
    profile = request.user.profile

    # =====================================================
    # 1. ACCESS CHECK
    # =====================================================
    if not profile.can_access_sacco_services():
        messages.warning(
            request,
            "Please update your profile and accept the member declaration to continue."
        )
        return redirect('member_declaration_view')

    # =====================================================
    # 2. BLOCK FAILED APPLICATIONS
    # =====================================================
    failed_loan_exists = Loan.objects.filter(
        member=profile,
        status='failed',
        rejection_reason__icontains='1/3'
    ).exists()

    if failed_loan_exists:
        messages.error(
            request,
            "Your previous loan failed the Kenyan 1/3 salary rule. "
            "Please wait for HR salary adjustment before applying again."
        )
        return redirect('member_dashboard')

    # =====================================================
    # 3. ACTIVE LOAN CHECK (only approved/disbursed, exclude replaced)
    # =====================================================
    active_loan = Loan.objects.filter(
        member=profile,
        status__in=['approved', 'disbursed']
    ).exclude(status='replaced').first()   # ← exclude replaced loans

    current_balance = Decimal('0.00')
    if active_loan:
        current_balance = Decimal(active_loan.get_remaining_balance())

    # =====================================================
    # 4. TOTAL SAVINGS & BORROWING POWER
    # =====================================================
    total_savings = CapitalShare.objects.filter(
        member=profile
    ).aggregate(
        Sum('amount')
    )['amount__sum'] or Decimal('0.00')

    global_cap = Decimal(total_savings)   # borrowing power = total shares

    # =====================================================
    # 5. OTHER EXPOSURE (pending loans)
    # =====================================================
    other_exposure = Loan.objects.filter(
        member=profile,
        status__in=['pending_hr_update', 'pending']
    ).aggregate(
        Sum('amount')
    )['amount__sum'] or Decimal('0.00')

    # =====================================================
    # 6. AVAILABLE LIMIT
    # =====================================================
    available_limit = global_cap - current_balance - Decimal(other_exposure)
    if available_limit < 0:
        available_limit = Decimal('0.00')

    # =====================================================
    # 7. POST REQUEST
    # =====================================================
    if request.method == 'POST':
        form = LoanApplicationForm(request.POST)
        if form.is_valid():
            loan = form.save(commit=False)
            loan.member = profile

            # ---- Check if top‑up is requested ----
            is_top_up = request.POST.get('is_top_up') == 'on'

            additional_amount = Decimal(loan.amount)   # the amount entered in the form

            if is_top_up and active_loan:
                # ✅ TOP‑UP: total principal = remaining balance + new amount
                total_principal = current_balance + additional_amount

                loan.is_topup = True
                loan.replaces_loan = active_loan
                loan.amount = total_principal           # set the combined principal
            else:
                total_principal = additional_amount
                loan.is_topup = False
                loan.replaces_loan = None

            duration = int(loan.duration_months)

            # =================================================
            # HR SALARY CHECK
            # =================================================
            if (
                not profile.gross_salary
                or profile.gross_salary <= 0
                or profile.salary_needs_review
            ):
                loan.status = 'pending_hr_update'
                loan.save()

                HRNotification.objects.get_or_create(
                    member=profile,
                    is_read=False,
                    defaults={
                        "member": profile,
                        "message": (
                            f"{profile.user.get_full_name()} "
                            f"requires HR salary update before loan processing."
                        )
                    }
                )

                messages.warning(
                    request,
                    "Loan submitted but awaiting HR salary update."
                )
                return redirect('member_dashboard')

            # =================================================
            # CONTRACT CHECK
            # =================================================
            if profile.employment_status == 'CONTRACT':
                if not profile.contract_expiry:
                    messages.error(request, "Contract expiry missing.")
                    return redirect('member_dashboard')

                max_allowed_date = profile.contract_expiry - relativedelta(months=2)
                loan_end_date = date.today() + relativedelta(months=duration)

                if loan_end_date > max_allowed_date:
                    messages.error(
                        request,
                        f"Loan must end by {max_allowed_date.strftime('%B %Y')}."
                    )
                    return redirect('member_dashboard')

            # =================================================
            # DURATION RULES (max 24 months)
            # =================================================
            if duration > 24:
                messages.error(
                    request,
                    "Welfare support loans have a maximum duration of 24 months."
                )
                return redirect('member_dashboard')

            # =================================================
            # 1/3 SALARY RULE (using total_principal)
            # =================================================
            gross = Decimal(profile.gross_salary or 0)
            monthly_installment = total_principal / Decimal(duration) if duration > 0 else Decimal(0)
            minimum_net_allowed = gross / Decimal('3')
            max_allowed_deduction = gross - minimum_net_allowed

            if monthly_installment > max_allowed_deduction:
                loan.status = 'failed'
                loan.rejection_reason = "Loan failed Kenyan 1/3 salary rule."
                loan.save()

                messages.error(
                    request,
                    f"Loan violates 1/3 rule. Installment {monthly_installment:,.2f} "
                    f"exceeds allowed {max_allowed_deduction:,.2f}."
                )
                return redirect('member_dashboard')

            # =================================================
            # LIMIT CHECK (using total_principal)
            # =================================================
            if total_principal > available_limit:
                messages.error(
                    request,
                    f"Loan limit exceeded. Available: {available_limit:,.2f}"
                )
                return redirect('member_dashboard')

            # =================================================
            # SAVE TRANSACTION
            # =================================================
            try:
                with transaction.atomic():
                    # Set status to pending for approval flow
                    loan.status = 'pending'
                    loan.interest = Decimal('0.00')
                    loan.insurance = Decimal('0.00')
                    loan.admin_approved = False
                    loan.staff_approved = False
                    loan.treasurer_approved = False

                    loan.save()

                    # ✅ If top‑up, close the old loan
                    if loan.is_topup and loan.replaces_loan:
                        old_loan = loan.replaces_loan
                        old_loan.status = 'replaced'   # or 'completed'
                        old_loan.save()

                messages.success(
                    request,
                    "Your welfare support request has been submitted for approval successfully!"
                )
                return redirect('member_dashboard')

            except Exception as e:
                messages.error(request, f"Transaction Error: {str(e)}")
                return redirect('member_dashboard')

        else:
            messages.error(request, "Please fix the form errors below.")

    else:
        form = LoanApplicationForm()

    context = {
        'loan_limit': available_limit,
        'global_cap': global_cap,
        'current_balance': current_balance,
        'total_savings': total_savings,
        'other_exposure': other_exposure,
        'form': form,
        'active_loan': active_loan,
    }
    return render(request, 'apply_loan.html', context)

def approve_xmas_loan(request, loan_id):
    loan = get_object_or_404(XmasLoan, id=loan_id)
    user = request.user
    u_type = getattr(user, 'user_type', None)

    # ❌ Prevent approving finalized loans
    if loan.status in ['rejected', 'approved']:
        messages.error(request, "This holiday loan is already finalized.")
        return redirect('staff_dashboard')

    # ---------------------------------------------------------
    # 1️⃣ STAFF FIRST (Type '2')
    # ---------------------------------------------------------
    if u_type == '2':
        loan.staff_approved = True
        loan.status = "partially_approved"
        loan.save()
        messages.success(request, "Staff approval recorded.")
        return redirect('staff_dashboard')

    # ---------------------------------------------------------
    # 2️⃣ TREASURER SECOND (Type '3')
    # ---------------------------------------------------------
    elif u_type == '3':
        if not loan.staff_approved:
            messages.error(request, "Wait for Staff to approve this holiday loan first.")
            return redirect('staff_dashboard')

        loan.treasurer_approved = True
        loan.status = "partially_approved"
        loan.save()
        messages.success(request, "Treasurer approval recorded.")
        return redirect('treasurer_dashboard')

    # ---------------------------------------------------------
    # 3️⃣ ADMIN LAST / FINAL (Type '1')
    # ---------------------------------------------------------
    elif u_type == '1' or user.is_superuser:
        if not (loan.staff_approved and loan.treasurer_approved):
            messages.error(request, "Staff and Treasurer must sign off before final approval.")
            return redirect('admin_dashboard')

        with transaction.atomic():
            loan.admin_approved = True
            loan.status = "approved"
            loan.approval_date = timezone.now()

            # --- X-MASS CALCULATIONS (Fixed 25.9% Interest, 3 Months) ---
            principal = Decimal(str(loan.amount_requested))
            interest_rate = Decimal('0.259') 
            duration_months = 3

            total_interest = principal * interest_rate
            total_payable = principal + total_interest
            monthly_installment = total_payable / Decimal(str(duration_months))

            # --- GENERATE 3-MONTH SCHEDULE ---
            # Clean old schedules if they exist
            LoanRepaymentSchedule.objects.filter(loan_id=loan.id, is_xmas=True).delete()

            for i in range(1, duration_months + 1):
                LoanRepaymentSchedule.objects.create(
                    xmas_loan=loan,
                    loan=None,# Link to the Xmas loan
                    installment_number=i,
                    due_date=loan.approval_date.date() + relativedelta(months=i),
                    amount_due=monthly_installment,
                    is_paid=False,
                    is_xmas=True # Helpful flag to distinguish from regular loans
                )

            loan.save()

        messages.success(request, f"X-Mass Loan Fully Approved! Total: KES {total_payable:,.2f}")
        return redirect('admin_dashboard')

    return redirect('member_dashboard')
def approve_xmas_loan(request, loan_id):
    loan = get_object_or_404(XmasLoan, id=loan_id)
    user = request.user
    u_type = getattr(user, 'user_type', None)

    # ❌ Prevent approving finalized loans
    if loan.status in ['rejected', 'approved']:
        messages.error(request, "This holiday loan is already finalized.")
        return redirect('staff_dashboard')

    # ---------------------------------------------------------
    # 1️⃣ STAFF FIRST (Type '2')
    # ---------------------------------------------------------
    if u_type == '2':
        loan.staff_approved = True
        loan.status = "partially_approved"
        loan.save()
        messages.success(request, "Staff approval recorded.")
        return redirect('staff_dashboard')

    # ---------------------------------------------------------
    # 2️⃣ TREASURER SECOND (Type '3')
    # ---------------------------------------------------------
    elif u_type == '3':
        if not loan.staff_approved:
            messages.error(request, "Wait for Staff to approve this holiday loan first.")
            return redirect('staff_dashboard')

        loan.treasurer_approved = True
        loan.status = "partially_approved"
        loan.save()
        messages.success(request, "Treasurer approval recorded.")
        return redirect('treasurer_dashboard')

    # ---------------------------------------------------------
    # 3️⃣ ADMIN LAST / FINAL (Type '1')
    # ---------------------------------------------------------
    elif u_type == '1' or user.is_superuser:
        if not (loan.staff_approved and loan.treasurer_approved):
            messages.error(request, "Staff and Treasurer must sign off before final approval.")
            return redirect('admin_dashboard')

        with transaction.atomic():
            loan.admin_approved = True
            loan.status = "approved"
            loan.approval_date = timezone.now()

            # --- X-MASS CALCULATIONS (Fixed 25.9% Interest, 3 Months) ---
            principal = Decimal(str(loan.amount_requested))
            interest_rate = Decimal('0.259') 
            duration_months = 3

            total_interest = principal * interest_rate
            total_payable = principal + total_interest
            monthly_installment = total_payable / Decimal(str(duration_months))

            # --- GENERATE 3-MONTH SCHEDULE ---
            # Clean old schedules if they exist
            LoanRepaymentSchedule.objects.filter(loan_id=loan.id, is_xmas=True).delete()

            for i in range(1, duration_months + 1):
                LoanRepaymentSchedule.objects.create(
                    xmas_loan=loan,
                    loan=None,# Link to the Xmas loan
                    installment_number=i,
                    due_date=loan.approval_date.date() + relativedelta(months=i),
                    amount_due=monthly_installment,
                    is_paid=False,
                    is_xmas=True # Helpful flag to distinguish from regular loans
                )

            loan.save()

        messages.success(request, f"X-Mass Loan Fully Approved! Total: KES {total_payable:,.2f}")
        return redirect('admin_dashboard')

    return redirect('member_dashboard')

def reject_xmas_loan(request, loan_id):
    """If any official rejects, the application status is set to 'rejected'."""
    loan = get_object_or_404(XmasLoan, id=loan_id)
    user = request.user
    u_type = getattr(user, 'user_type', None)
    
    loan.status = 'rejected'
    loan.save()
    
    messages.warning(request, "Holiday loan application has been rejected.")
    
    # Finalized Redirection logic
    if u_type == '1' or user.is_superuser:
        return redirect('admin_dashboard')
    elif u_type == '2':
        return redirect('staff_dashboard')  
    elif u_type == '3':
        return redirect('treasurer_dashboard') # Fixed typo and changed to redirect
    
    return redirect('member_dashboard')


@login_required
@role_required(allowed_roles=['3'])  # Treasurer only
def loan_detail(request, loan_id):
    loan = get_object_or_404(Loan, id=loan_id)

    guarantors = Guarantor.objects.filter(loan=loan)

    return render(request, 'dat.html', {
        'loan': loan,
        'guarantors': guarantors,
    })

def calculate_penalty(loan):
    overdue_schedules = LoanRepaymentSchedule.objects.filter(
        loan=loan,
        is_paid=False,
        due_date__lt=date.today()
    )
    
    penalty_rate = Decimal('0.02')  # 2% per month
    total_penalty = Decimal('0.00')
    
    for installment in overdue_schedules:
        months_overdue = (date.today().year - installment.due_date.year) * 12 + (date.today().month - installment.due_date.month)
        if months_overdue > 0:
            total_penalty += installment.amount_due * penalty_rate * months_overdue
    
    return total_penalty

@login_required
def pay_loan(request):
    profile = request.user.profile

    # ===== WELFARE: Get ALL active loans for the member =====
    active_loans = Loan.objects.filter(
        member=profile,
        status__in=['disbursed']
    ).order_by('-id')

    # ===== WELFARE: Prepare a list of loan data for the UI =====
    loans_data = []

    for loan in active_loans:
        
        # ===== WELFARE: No penalties (0% interest, no penalties) =====
        total_penalty = Decimal('0.00')
        
        # ===== WELFARE: Total payable is just the principal =====
        total_payable = loan.amount  # Principal only (no interest, no insurance)
        
        # ===== WELFARE: Total repaid =====
        total_repaid = LoanRepayment.objects.filter(
            loan=loan
        ).aggregate(
            Sum('amount_paid')
        )['amount_paid__sum'] or Decimal('0.00')
        
        # ===== WELFARE: Remaining balance =====
        remaining_balance = max(total_payable - total_repaid, Decimal('0.00'))
        
        # ===== WELFARE: Next installment =====
        # For welfare loans, the next installment is calculated based on the schedule
        next_installment = None
        if loan.duration_months and loan.duration_months > 0:
            # Calculate monthly installment amount
            monthly_installment = loan.amount / Decimal(loan.duration_months)
            
            # Get the next due date based on application date
            from dateutil.relativedelta import relativedelta
            next_due_date = loan.application_date.date() + relativedelta(months=1)
            
            # Find the next unpaid schedule
            next_schedule = LoanRepaymentSchedule.objects.filter(
                loan=loan,
                is_paid=False
            ).order_by('due_date').first()
            
            if next_schedule:
                next_installment = next_schedule
            else:
                # If no schedule exists, create a virtual one
                # This is a fallback for loans without schedules
                next_installment = {
                    'amount_due': monthly_installment,
                    'due_date': next_due_date
                }
        
        # ===== WELFARE: Progress calculation =====
        progress = (total_repaid / total_payable * 100) if total_payable > 0 else 0
        
        loans_data.append({
            'loan': loan,
            'remaining_balance': remaining_balance,
            'next_installment': next_installment,
            'total_penalty': total_penalty,  # Always 0
            'progress': progress,
            'total_payable': total_payable,
            'total_repaid': total_repaid,
        })

    return render(request, 'pay_loan.html', {'loans_data': loans_data})
@role_required(allowed_roles=['3'])  # Only Treasurer
def treasurer_pay_Xloan(request, loan_id):
    loan = get_object_or_404(XmasLoan, id=loan_id)

    if request.user.user_type != '3':  # Only Treasurer
        messages.error(request, "Unauthorized access")
        return redirect('treasurer_dashboard')

    # ===== Calculate monthly installment =====
    monthly_installment = Decimal('0.00')
    if loan.installments and loan.installments > 0:
        monthly_installment = loan.total_payable / Decimal(loan.installments)

    if request.method == "POST":
        try:
            amount = Decimal(request.POST.get('amount'))

            with transaction.atomic():
                # 1️⃣ Record repayment
                repayment = LoanRepayment.objects.create(
                    xmas_loan=loan,
                    is_xmas=True,
                    member=loan.member,
                    amount_paid=amount,
                    reference=generate_transaction_ref("TR")
                )

                # 2️⃣ Apply to repayment schedule
                amount_to_distribute = amount
                schedules = LoanRepaymentSchedule.objects.filter(
                    xmas_loan=loan, is_paid=False, is_xmas=True
                ).order_by('due_date')

                for installment in schedules:
                    if amount_to_distribute <= 0:
                        break
                    if amount_to_distribute >= installment.amount_due:
                        amount_to_distribute -= installment.amount_due
                        installment.is_paid = True
                        installment.save()
                    else:
                        # Partial payment
                        installment.amount_due -= amount_to_distribute
                        installment.save()
                        amount_to_distribute = Decimal('0.00')
                        break

                # 3️⃣ Excess goes to savings
                if amount_to_distribute > 0:
                    MonthlyContribution.objects.create(
                        member=loan.member,
                        amount=amount_to_distribute,
                        month=timezone.now().date()
                    )

                # 4️⃣ Update loan status
                total_payable = LoanRepaymentSchedule.objects.filter(
                    xmas_loan=loan
                ).aggregate(Sum('amount_due'))['amount_due__sum'] or Decimal('0.00')

                if loan.total_paid >= total_payable:
                    loan.status = 'completed'
                    loan.is_disbursed = True
                    loan.save()

                # 5️⃣ Log transaction
                Transaction.objects.create(
                    member=loan.member,
                    transaction_type='repayment',
                    amount=amount,
                    reference=repayment.reference
                )

            messages.success(request, f"Payment of KES {amount:,.2f} recorded for {loan.member.user.get_full_name()}")
            return redirect('treasurer_dashboard')

        except Exception as e:
            messages.error(request, f"Error processing payment: {str(e)}")

    context = {
        'loan': loan,
        'monthly_installment': monthly_installment,
    }
    return render(request, "treasurer_pay.html", context)
@login_required
@role_required(allowed_roles=['1','3'])
def treasurer_pay_loan(request, loan_id):
    loan = get_object_or_404(Loan, id=loan_id)

    # Access control
    if request.user.is_superuser and request.user.user_type != '3':
        messages.error(request, "Unauthorized access: Treasurer permissions required.")
        return redirect('treasurer_dashboard')

    # Calculate remaining balance for display
    total_paid = LoanRepayment.objects.filter(loan=loan).aggregate(Sum('amount_paid'))['amount_paid__sum'] or Decimal('0.00')
    remaining_balance = max(loan.total_payable - total_paid, Decimal('0.00'))

    if request.method == "POST":
        try:
            amount = Decimal(request.POST.get('amount', '0'))
            if amount <= 0:
                messages.error(request, "Invalid amount. Enter a positive value.")
                return redirect('treasurer_pay_loan', loan_id=loan.id)

            with transaction.atomic():
                # Record repayment
                repayment = LoanRepayment.objects.create(
                    loan=loan,
                    member=loan.member,
                    amount_paid=amount,
                    reference=generate_transaction_ref("TR"),
                    is_xmas=False
                )

                # Amortise against schedule
                amount_to_distribute = amount
                schedules = LoanRepaymentSchedule.objects.filter(
                    loan=loan, is_paid=False
                ).order_by('due_date')

                for installment in schedules:
                    if amount_to_distribute <= 0:
                        break
                    if amount_to_distribute >= installment.amount_due:
                        amount_to_distribute -= installment.amount_due
                        installment.is_paid = True
                        installment.date_paid = timezone.now()
                        installment.save()
                    else:
                        # Partial payment: mark the installment partially paid?
                        # We'll keep it simple: only full instalments are marked.
                        # The remaining amount will carry over as overpayment (or not).
                        # We won't change the current logic.
                        break

                # Update loan status if fully paid
                total_paid_after = LoanRepayment.objects.filter(loan=loan).aggregate(Sum('amount_paid'))['amount_paid__sum'] or Decimal('0.00')
                if total_paid_after >= loan.total_payable:
                    loan.status = 'completed'
                    loan.save()

                # Transaction log
                Transaction.objects.create(
                    member=loan.member,
                    transaction_type='repayment',
                    amount=amount,
                    reference=repayment.reference
                )

            messages.success(request, f"Successfully processed KES {amount} for {loan.member.user.get_full_name()}.")
            return redirect('treasurer_dashboard')

        except Exception as e:
            messages.error(request, f"Error: {str(e)}")

    context = {
        'loan': loan,
        'remaining_balance': remaining_balance,
        'total_paid': total_paid,
        'monthly_installment': loan.monthly_installment,
        'total_payable': loan.total_payable,
    }
    return render(request, "treasurer_pay_loan.html", context)

@login_required
@role_required(allowed_roles=['2', '4'])  # Staff and Admin
def staff_dashboard(request):
    # Ensure only staff can access
    if not request.user.is_authenticated:
        return redirect('login')  # redundant with @login_required but safe

    if request.user.user_type != '2' and not request.user.is_superuser:
        
        return redirect('access_denied')  # Redirect to an access denied page or show message
    pending_shares_refunds = CapitalShareRefund.objects.filter(
        status__in =['pending'],
        treasurer_approved=False
    ).order_by('-date_applied')
    # Your dashboard logic here
    pending_loans = Loan.objects.filter(
        staff_approved=False,
        status__in=['pending', 'partially_approved']
    ).order_by('-application_date')
    pending_xmas_loans = XmasLoan.objects.filter(status='pending').order_by('-application_date')

    total_savings_pool = MonthlyContribution.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    total_members = Profile.objects.count()
    total_interest_earned = LoanRepaymentSchedule.objects.filter(is_paid=True).aggregate(Sum('amount_due'))['amount_due__sum'] or 0
    pending_xmas_refunds = XmasRefund.objects.filter(
        status__in=['pending', 'partially_refunded']
    )
    context = {
        'pending_xmas_refunds': pending_xmas_refunds,
        'pending_loans': pending_loans,
        'total_savings_pool': total_savings_pool,
        'total_members': total_members,
        'total_interest_earned': total_interest_earned,
        'pending_xmas_loans': pending_xmas_loans,
        'pending_shares_refunds': pending_shares_refunds,
    }

    return render(request, 'stf.html', context)
def rejected_loans_view(request):
    rejected_loans = Loan.objects.filter(status='rejected')
    context = {
        'rejected_loans': rejected_loans
    }
    return render(request, 'rejected_loans.html', context)
def Completed_loans(request):
    complete=Loan.objects.filter(status="completed")
    context={
        'complete':complete
        
    }
    return render (request, 'complet.html',context)
def approved_loans_view(request):
    approved_loans = Loan.objects.filter(status='approved')
    # Check the fields available on the first object
    if approved_loans.exists():
        print(dir(approved_loans.first())) 
    
    context = {'approved_loans': approved_loans}
    return render(request, 'approved_loan.html', context)
def Xm_approved(request):
    # Get loans that are fully approved (all 3 approvals) OR have status='approved'
    approved_loans = XmasLoan.objects.filter(
        admin_approved=True,
        staff_approved=True,
        treasurer_approved=True
    ).exclude(status__in=['rejected', 'cleared', 'disbursed'])
    
    # Also include loans where status is 'approved'
    status_approved = XmasLoan.objects.filter(status='approved').exclude(status__in=['rejected', 'cleared', 'disbursed'])
    
    # Combine both querysets
    approved_loans = (approved_loans | status_approved).distinct()
    
    # ===== FIX: Don't assign to approval_progress, just use it in template =====
    # The property will be calculated automatically when accessed in the template
    
    context = {
        'approved_loans': approved_loans
    }
    return render(request, 'approved_Xm.html', context)
def pending_loans_view(request):
    pending_loans = Loan.objects.filter(status='pending')
    context = {
        'pending_loans': pending_loans
    }
    return render(request, 'pending_loans.html', context)
def active_xmas_loan(request):
    # This covers both the string status and the boolean flag
    xm_active = XmasLoan.objects.filter(status='disbursed', is_disbursed=True)
    return render(request, 'xm_active.html', {'xm_active': xm_active})
@transaction.atomic
def disburse_loan_xmass(request, loan_id):
    loan = get_object_or_404(XmasLoan, id=loan_id)

    # 1. Validation: Use the new property to check for the 3 sign-offs
    if loan.approval_progress < 3:
        messages.error(request, "This loan requires Staff, Treasurer, and Admin approval before disbursement.")
        return redirect('treasurer_dashboard')

    if loan.is_disbursed:
        messages.warning(request, "This loan has already been disbursed.")
        return redirect('treasurer_dashboard')

    # 2. Update Loan Record
    loan.is_disbursed = True
    loan.status = 'disbursed'
    loan.disbursement_date = timezone.now()
    loan.save()

    # 3. Financial Record
    # Note: Using amount_requested as per your XmasLoan model
    record_transaction(
        member_profile=loan.member,
        type='loan_disbursement',
        amount=loan.amount_requested,
        reference=f"XMASS-{loan.id}-{timezone.now().year}"
    )

    messages.success(request, f"Successfully disbursed KES {loan.amount_requested} to {loan.member}.")
    return redirect('treasurer_dashboard')
def active_loan(request):
    # Filter for disbursed loans
    active_loans = Loan.objects.filter(status='disbursed')
    
    context = {
        "active_loans": active_loans # Changed from 'active_lons'
    }
    return render(request, 'active.html', context)
def monthly_repayment_report(request):
    prof = Profile.objects.all()
    report_data = LoanRepayment.objects.annotate(
        month=TruncMonth('payment_date')
    ).values(
        'month',
        'member__user__first_name',
        'member__user__last_name',
        'member__pf_number',  # <-- Add this
        'loan__id'
    ).annotate(
        total_paid=Sum('amount_paid')
    ).order_by('-month')

    context = {
        'report_data': report_data,
        'prof': prof
    }
    return render(request, 'report.html', context)

@login_required
@role_required(allowed_roles=['1','3'])  # Treasurer only
def treasurer_dashboard(request):
    # 1. Security Check (Uncommented for safety)
    if getattr(request.user, 'user_type', None) != '3' and not request.user.is_superuser:
        return redirect('access_denied')  # Redirect to an access denied page or show message

    # 2. Filter loans specifically awaiting THIS treasurer's signature
    # We look for loans that are not yet approved by treasurer but aren't rejected
    awaiting_treasurer = Loan.objects.filter(
        treasurer_approved=False, 
        status__in=['pending', 'partially_approved']
    ).order_by('-application_date')

    # 3. Financial Calculations
    # Using Decimal('0') ensures compatibility with DecimalField in models
    total_savings = MonthlyContribution.objects.aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
    total_shares = CapitalShare.objects.aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
    active_loans_value = Loan.objects.filter(
    is_disbursed=True
).aggregate(total=Sum('amount'))['total'] or Decimal('0')   
    # Calculate Interest Earned (Payments made minus estimated principal portion or just total interest collected)
    total_interest_earned = LoanRepaymentSchedule.objects.filter(is_paid=True).aggregate(Sum('amount_due'))['amount_due__sum'] or Decimal('0')
    pending_xmas_loans = XmasLoan.objects.filter(
        status__in=['pending', 'partially_approved'], 
        treasurer_approved=False
        
    )
    pending_shares_refunds = CapitalShareRefund.objects.filter(
        status__in = ['staff_approved'],
        treasurer_approved=False)
    pending_xmas_refunds = XmasRefund.objects.filter(
        status__in=['pending', 'partially_approved']
    )
    # Ca
    # lculate Liquidity
    total_repayments = LoanRepayment.objects.aggregate(Sum('amount_paid'))['amount_paid__sum'] or Decimal('0')
    
    # Formula: (Money In) - (Money Out)
    available_cash = (total_savings + total_shares + total_repayments) - active_loans_value

    # 4. Recent Activity
    recent_transactions = Transaction.objects.all().order_by('-created_at')[:10]

    context = {
        'pending_shares_refunds': pending_shares_refunds,
        'pending_xmas_loans': pending_xmas_loans,
        'awaiting_treasurer': awaiting_treasurer,
        'total_savings': total_savings,
        'total_shares': total_shares,
        'active_loans_value': active_loans_value,
        'available_cash': available_cash,
        'total_interest': total_interest_earned,
        'recent_transactions': recent_transactions,
        'pending_xmas_refunds': pending_xmas_refunds,
    }

    return render(request, 'treasurer_dashboard.html', context)



def all_savings(request):
    savings = MonthlyContribution.objects.all()
    total_savings = savings.aggregate(total=Sum('amount'))['total'] or 0
    capita_savings=CapitalShare.objects.all()
    total_capita_savings = capita_savings.aggregate(total=Sum('amount'))['total'] or 0
    total_savings += total_capita_savings
    available_cash = total_savings - Loan.objects.filter(is_disbursed=True).aggregate(total=Sum('amount'))['total'] or Decimal('0')

    context = {
        'savings': savings,
        'total_savings': total_savings,
        'available_cash': available_cash
    }
    return render(request, 'sav.html', context)

def my_savings(request):
    profile = request.user.profile

    savings = MonthlyContribution.objects.filter(member=profile).order_by('-month')

    total_savings = savings.aggregate(total=Sum('amount'))['total'] or 0

    context = {
        'savings': savings,
        'total_savings': total_savings
    }

    return render(request, 'mysaving.html', context)
@login_required
def my_loans(request):
    profile = request.user.profile

    # Only loans for this member, ordered by newest first
    loans = Loan.objects.filter(member=profile).order_by('-application_date')

    context = {
        'loans': loans
    }
    return render(request, 'my_loans.html', context)
def my_shares(request):
    profile = request.user.profile

    shares = CapitalShare.objects.filter(member=profile).order_by('-date_paid')

    total_shares = shares.aggregate(total=Sum('amount'))['total'] or 0

    context = {
        'shares': shares,
        'total_shares': total_shares
    }

    return render(request, 'my_shares.html', context)
# @login_required
def approve_loan(request, loan_id):
    loan = get_object_or_404(Loan, id=loan_id)
    user = request.user
    u_type = getattr(user, 'user_type', None)

    # ❌ Prevent approving rejected or already approved loans
    if loan.status in ['rejected', 'approved']:
        messages.error(request, "Loan already finalized.")
        return redirect('member_dashboard')

    # -------------------------
    # ✅ ENFORCE APPROVAL ORDER
    # -------------------------

    # 1️⃣ STAFF FIRST
    if u_type == '2':
        loan.staff_approved = True
        loan.status = "partially_approved"
        loan.save()
        messages.success(request, "Staff approved.")
        return redirect('staff_dashboard')

    # 2️⃣ TREASURER SECOND (only after staff)
    elif u_type == '3':
        if not loan.staff_approved:
            messages.error(request, "Staff must approve first.")
            return redirect('treasurer_dashboard')

        loan.treasurer_approved = True
        loan.status = "partially_approved"
        loan.save()
        messages.success(request, "Treasurer approved.")
        return redirect('treasurer_dashboard')

    # 3️⃣ ADMIN LAST (FINAL)
    elif u_type == '1' or user.is_superuser:
        if not (loan.staff_approved and loan.treasurer_approved):
            messages.error(request, "Staff and Treasurer must approve first.")
            return redirect('admin_dashboard')

        # -------------------------
        # ✅ FINAL APPROVAL
        # -------------------------
        with transaction.atomic():
            loan.admin_approved = True
            loan.status = "approved"
            loan.approval_date = timezone.now()

            # --- CALCULATIONS ---
            principal = Decimal(str(loan.amount))
            interest_rate = Decimal(0)
            duration_years = Decimal(str(loan.duration_months)) / Decimal('12')

            total_interest = principal * interest_rate * duration_years
            insurance =0
            total_payable = principal + total_interest + insurance
            monthly_installment = total_payable / Decimal(str(loan.duration_months))

            # --- SCHEDULE ---
            LoanRepaymentSchedule.objects.filter(loan=loan).delete()

            for i in range(1, loan.duration_months + 1):
                LoanRepaymentSchedule.objects.create(
                    loan=loan,
                    installment_number=i,
                    due_date=loan.approval_date.date() + relativedelta(months=i),
                    amount_due=monthly_installment,
                    is_paid=False
                )

            loan.save()

        messages.success(
            request,
            f"Loan Fully Approved! Total: KES {total_payable:,.2f}"
        )
        return redirect('admin_dashboard')

    return redirect('member_dashboard')
@login_required
def reject_loan(request, loan_id):
    loan = get_object_or_404(Loan, id=loan_id)
    user = request.user

    # ❌ stop if already finalized
    if loan.status in ['approved', 'rejected']:
        messages.error(request, "Loan already finalized.")
        return redirect('member_dashboard')

    # 🔴 ONE REJECTION = FULL REJECTION
    loan.status = "rejected"
    loan.save()

    messages.error(request, "Loan rejected.")

    u_type = getattr(user, 'user_type', None)
    if user.is_superuser or u_type == '1': 
        return redirect('admin_dashboard')
    if u_type == '2': 
        return redirect('staff_dashboard')
    if u_type == '3': 
        return redirect('treasurer_dashboard')

    return redirect('member_dashboard')
def record_transaction(member_profile, type, amount, reference=None, loan=None):
    if not reference:
        # Map transaction types to prefixes
        prefixes = {'deposit': 'DEP', 'repayment': 'REP', 'shares': 'SHR'}
        prefix = prefixes.get(type, 'TX')
        reference = generate_transaction_ref(prefix)
    
    with transaction.atomic():
        return Transaction.objects.create(
            member=member_profile,
            transaction_type=type,
            amount=amount,
            reference=reference
        )


@login_required
def disburse_loan(request, loan_id):
    loan = get_object_or_404(Loan, id=loan_id)

    if loan.status != 'approved':
        messages.error(request, "Loan must be approved first.")
        return redirect('treasurer_dashboard')

    if loan.is_disbursed:
        messages.warning(request, "Loan already disbursed.")
        return redirect('treasurer_dashboard')

    with transaction.atomic():
        loan.is_disbursed = True
        loan.status = 'disbursed'   # 🔥 ADD THIS
        loan.disbursed_at = timezone.now()
        loan.save()

        # Record transaction (money leaving SACCO)
        record_transaction(
            member_profile=loan.member,
            type='loan_disbursement',
            amount=loan.amount,
            reference=f"DISB-Loan#{loan.id}"
        )

    messages.success(request, "Loan disbursed successfully.")
    return redirect('treasurer_dashboard')
import json
import logging
import uuid
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.utils import timezone
from django.http import JsonResponse
import requests
from .models import Profile, PendingMpesaTransaction, CapitalShare, MonthlyContribution, Loan, XmasLoan, LoanRepayment, BereavementPayment, BereavementAnnouncement, Transaction
from .mpesa_utils import get_mpesa_access_token, get_mpesa_password

logger = logging.getLogger(__name__)

@login_required
def initiate_stk_push(request):
    if request.method == "POST":
        payment_type = request.POST.get('payment_type')
        amount_str = request.POST.get('amount')
        member_id = request.POST.get('member_id')
        loan_id = request.POST.get('loan_id')
        
        logger.info(f"🔵🔵🔵 INITIATE_STK_PUSH CALLED")
        logger.info(f"🔵 POST data: {request.POST}")
        logger.info(f"🔵 User: {request.user}")
        
        # 1. Validation
        if not amount_str or not amount_str.strip():
            messages.error(request, "Please enter a valid amount.")
            return redirect(request.META.get('HTTP_REFERER', 'member_dashboard'))
            
        try:
            amount = float(amount_str)
        except ValueError:
            messages.error(request, "Invalid amount format.")
            return redirect(request.META.get('HTTP_REFERER', 'member_dashboard'))

        # 2. Get User/Member
        target_profile = get_object_or_404(Profile, id=member_id) if member_id else request.user.profile
        phone = target_profile.phone_number 
        
        # Format phone
        if phone.startswith('0'):
            phone = '254' + phone[1:]
        elif not phone.startswith('254'):
            phone = '254' + phone
            
        access_token = get_mpesa_access_token()
        password, timestamp = get_mpesa_password()
        
        if not access_token:
            messages.error(request, "M-Pesa authentication failed.")
            return redirect('member_dashboard')

        # 3. Account Reference – accept multiple aliases
        if payment_type in ('shares', 'share'):
            account_ref = f"SH{target_profile.id}"
            description = "Shares Payment"
        elif payment_type in ('savings', 'saving'):
            account_ref = f"SV{target_profile.id}"
            description = "Savings Payment"
        elif payment_type == 'bereavement':
            account_ref = f"BR{target_profile.id}"
            description = "Bereavement Payment"
        elif payment_type in ('xmas', 'xmas_repayment', 'xmas_loan'):
            if not loan_id:
                messages.error(request, "Loan ID is required for Xmas repayment.")
                return redirect(request.META.get('HTTP_REFERER', 'member_dashboard'))
            account_ref = f"XM{loan_id}"
            description = "Xmas Repayment"
        elif payment_type in ('loan', 'loan_repayment'):
            if not loan_id:
                messages.error(request, "Loan ID is required for loan repayment.")
                return redirect(request.META.get('HTTP_REFERER', 'member_dashboard'))
            account_ref = f"LN{loan_id}"
            description = "Loan Repayment"
        else:
            messages.error(request, "Invalid payment type.")
            return redirect(request.META.get('HTTP_REFERER', 'member_dashboard'))

        # 4. Create pending transaction BEFORE M-Pesa call
        pending_txn = None
        temp_checkout_id = None
        
        try:
            temp_checkout_id = f"TEMP_{uuid.uuid4().hex[:12]}"
            
            logger.info(f"🔵 Creating pending transaction with temp ID: {temp_checkout_id}")
            logger.info(f"🔵 Account Ref: {account_ref}, Member: {target_profile.id}, Type: {payment_type}, Amount: {amount}, Phone: {phone}")
            
            pending_txn = PendingMpesaTransaction.objects.create(
                checkout_request_id=temp_checkout_id,
                account_reference=account_ref,
                member=target_profile,
                payment_type=payment_type,
                amount=Decimal(str(amount)),
                loan_id=loan_id if loan_id else None,
                phone_number=phone,
                processed=False
            )
            logger.info(f"✅ Created pending transaction: ID={pending_txn.id}")
            
        except Exception as e:
            logger.error(f"❌ Error creating pending transaction: {str(e)}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            messages.error(request, f"Error creating pending record: {str(e)}")
            return redirect(request.META.get('HTTP_REFERER', 'member_dashboard'))

        # 5. API Request Body
        request_body = {
            "BusinessShortCode": "174379",
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount),
            "PartyA": phone,
            "PartyB": "174379",
            "PhoneNumber": phone,
            "CallBackURL": "https://scallop-epic-sandlot.ngrok-free.dev/mpesa_callback/",
            "AccountReference": account_ref[:12],
            "TransactionDesc": description[:13]
        }
        
        logger.info(f"🔵 STK Push Request Body: {request_body}")
        
        try:
            mpesa_endpoint = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
            response = requests.post(
                mpesa_endpoint,
                json=request_body,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            response_data = response.json()
            
            logger.info(f"🔵 M-Pesa STK Response: {json.dumps(response_data, indent=2)}")
            
            if response_data.get("ResponseCode") == "0":
                checkout_request_id = response_data.get('CheckoutRequestID')
                logger.info(f"🔵 CheckoutRequestID from M-Pesa: {checkout_request_id}")
                
                if pending_txn and checkout_request_id:
                    pending_txn.checkout_request_id = checkout_request_id
                    pending_txn.save()
                    logger.info(f"✅ Updated pending with real CheckoutID: {checkout_request_id}")
                
                messages.success(request, "M-Pesa prompt sent. Please check your phone.")
            else:
                error_msg = response_data.get('errorMessage') or response_data.get('CustomerMessage', 'Failed')
                logger.error(f"❌ M-Pesa Error: {error_msg}")
                messages.error(request, f"M-Pesa Error: {error_msg}")
                
                if pending_txn:
                    pending_txn.delete()
                    logger.info("✅ Deleted pending due to M-Pesa error")
                
        except Exception as e:
            logger.error(f"❌ STK Push Error: {str(e)}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            messages.error(request, f"Connection Error: {str(e)}")
            
            if pending_txn:
                pending_txn.delete()
                logger.info("✅ Deleted pending due to error")
        
        # 6. Redirection
        if request.user.groups.filter(name='Treasurer').exists():
            return redirect('treasurer_dashboard')
        return redirect('member_dashboard')
def download_receipt(request, saving_id):
    saving = get_object_or_404(MonthlyContribution, id=saving_id, member=request.user.profile)
    
    # Create the receipt content
    content = f"""
    =========================================
               ELDOPOLY SACCO RECEIPT
    =========================================
    Date: {saving.created_at.strftime('%Y-%m-%d %H:%M')}
    Member: {saving.member.user.get_full_name()}
    Member ID: #{saving.member.id}
    -----------------------------------------
    Transaction Type: MONTHLY SAVINGS
    Period: {saving.month.strftime('%B %Y')}
    Amount Paid: KES {saving.amount:,.2f}
    -----------------------------------------
    Thank you for saving with us!
    =========================================
    """
    
    response = HttpResponse(content, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="Receipt_{saving.id}.txt"'
    return response
def Setting_loan(request):
     pass
#

@login_required
def purchase_shares(request):
    user_profile = request.user.profile

    if request.method == "POST":
        form = SharesForm(request.POST)

        if form.is_valid():
            share = form.save(commit=False)
            share.member = user_profile
            share.save()

            messages.success(
                request,
                f"Share purchase of KES {share.amount} has been recorded."
            )
            return redirect("member_dashboard")
    else:
        form = SharesForm()

    return render(request, "shares.html", {"form": form})
    
    # If treasurer, we could later add manual + mpesa
    return redirect("treasurer_dashboard")
def LoanP(request):
    if request.method == "POST":
        form = LoanPurposeForm(request.POST)
        if form.is_valid():
            form.save()
            # Fixed the messages syntax error as well
            messages.success(request, "Saved successfully") 
            return redirect('admin_dashboard')
    else:
        # This handles the initial GET request
        form = LoanPurposeForm()
        
    # Now 'form' exists regardless of the request method
    return render(request, "p.html", {'form': form})
@login_required
@role_required(allowed_roles=['3'])
# from datetime import datetime

# from django.db import transaction
# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib import messages
# from django.utils import timezone

# from .models import Profile, Transaction
# from .forms import SharesForm
@login_required


def treasurer_purchase_shares(request, member_id):

    member_profile = get_object_or_404(
        Profile,
        id=member_id
    )

    if request.method == "POST":

        form = SharesForm(request.POST)

        if form.is_valid():

            try:

                with transaction.atomic():

                    share = form.save(commit=False)

                    share.member = member_profile

                    share.save()

                    # SAVE TRANSACTION
                    # USING SELECTED MONTH
                    Transaction.objects.create(
                        member=member_profile,
                        transaction_type='shares',
                        amount=share.amount,
                        created_at=timezone.make_aware(
                            datetime.combine(
                                share.month,
                                datetime.min.time()
                            )
                        )
                    )

                messages.success(
                    request,
                    f"KES {share.amount} shares recorded for "
                    f"{member_profile.user.get_full_name()}"
                )

                return redirect('Members')

            except Exception as e:

                messages.error(
                    request,
                    f"Database Error: {str(e)}"
                )

        else:

            messages.error(
                request,
                "Please correct the form errors."
            )

    else:

        form = SharesForm()

    return render(
        request,
        'treasurer_confirm_share.html',
        {
            'member': member_profile,
            'form': form
        }
    )
@login_required
#@role_required(allowed_roles=['1', '2', '3', '4'])  # Staff, Treasurer, Admin

def member_individual_report(request):
    # Get the profile of the currently logged-in user
    member = request.user.profile 
    
    # ===== SHARES =====
    shares = CapitalShare.objects.filter(member=member).order_by('-date_created')
    total_shares = shares.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    
    # ===== SHARE REFUNDS =====
    share_refunds = CapitalShareRefund.objects.filter(member=member).order_by('-date_applied')
    total_share_refunds = share_refunds.aggregate(Sum('amount_requested'))['amount_requested__sum'] or Decimal('0.00')
    pending_share_refunds = share_refunds.filter(status='pending').count()
    
    # ===== SAVINGS =====
    savings = MonthlyContribution.objects.filter(member=member).order_by('-created_at')
    total_savings = savings.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    
    # ===== LOANS (Regular) =====
    loans = Loan.objects.filter(member=member).order_by('-application_date')
    total_loans = loans.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    
    # Loan breakdown by status
    active_loans = loans.filter(status='disbursed')
    total_active_loans = active_loans.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    
    pending_loans = loans.filter(status='pending')
    total_pending_loans = pending_loans.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    
    completed_loans = loans.filter(status='completed')
    total_completed_loans = completed_loans.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    
    # ===== XMAS LOANS =====
    xmas_loans = XmasLoan.objects.filter(member=member).order_by('-application_date')
    total_xmas_loans = xmas_loans.aggregate(Sum('amount_requested'))['amount_requested__sum'] or Decimal('0.00')
    
    # Xmas loan breakdown
    active_xmas = xmas_loans.filter(status='disbursed')
    total_active_xmas = active_xmas.aggregate(Sum('amount_requested'))['amount_requested__sum'] or Decimal('0.00')
    
    pending_xmas = xmas_loans.filter(status='pending')
    total_pending_xmas = pending_xmas.aggregate(Sum('amount_requested'))['amount_requested__sum'] or Decimal('0.00')
    
    cleared_xmas = xmas_loans.filter(status='cleared')
    total_cleared_xmas = cleared_xmas.aggregate(Sum('amount_requested'))['amount_requested__sum'] or Decimal('0.00')
    
    # ===== REPAYMENTS =====
    repayments = LoanRepayment.objects.filter(member=member).order_by('-payment_date')
    total_repaid = repayments.aggregate(Sum('amount_paid'))['amount_paid__sum'] or Decimal('0.00')
    
    # Regular repayments
    regular_repayments = repayments.filter(is_xmas=False)
    total_regular_repaid = regular_repayments.aggregate(Sum('amount_paid'))['amount_paid__sum'] or Decimal('0.00')
    
    # Xmas repayments
    xmas_repayments = repayments.filter(is_xmas=True)
    total_xmas_repaid = xmas_repayments.aggregate(Sum('amount_paid'))['amount_paid__sum'] or Decimal('0.00')
    
    # ===== OUTSTANDING BALANCES =====
    # Regular loans outstanding
    total_loan_payable = sum([loan.total_payable for loan in loans if loan.status in ['disbursed', 'approved']])
    outstanding_regular = Decimal(total_loan_payable) - Decimal(total_regular_repaid)
    
    # Xmas loans outstanding
    total_xmas_payable = sum([xloan.total_payable for xloan in xmas_loans if xloan.status in ['disbursed', 'approved']])
    outstanding_xmas = Decimal(total_xmas_payable) - Decimal(total_xmas_repaid)
    
    total_outstanding = outstanding_regular + outstanding_xmas
    
    # ===== TRANSACTIONS =====
    transactions = Transaction.objects.filter(member=member).order_by('-created_at')
    total_transactions = transactions.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    
    # ===== BEREAVEMENT =====
    bereavement_payments = BereavementPayment.objects.filter(member=member).order_by('-payment_date')
    total_bereavement = bereavement_payments.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    
    # ===== EXPENSES (if member is admin/treasurer) =====
    expenses = []
    total_expenses = Decimal('0.00')
    if request.user.is_superuser or request.user.groups.filter(name='Treasurer').exists():
        expenses = Expense.objects.filter(recorded_by=member).order_by('-date_spent')
        total_expenses = expenses.aggregate(Sum('amount_spent'))['amount_spent__sum'] or Decimal('0.00')
    
    context = {
        # Member Info
        'member': member,
        
        # Shares
        'shares': shares,
        'total_shares': total_shares,
        
        # Share Refunds
        'share_refunds': share_refunds,
        'total_share_refunds': total_share_refunds,
        'pending_share_refunds': pending_share_refunds,
        
        # Savings
        'savings': savings,
        'total_savings': total_savings,
        
        # Loans
        'loans': loans,
        'total_loans': total_loans,
        'active_loans': active_loans,
        'total_active_loans': total_active_loans,
        'pending_loans': pending_loans,
        'total_pending_loans': total_pending_loans,
        'completed_loans': completed_loans,
        'total_completed_loans': total_completed_loans,
        
        # Xmas Loans
        'xmas_loans': xmas_loans,
        'total_xmas_loans': total_xmas_loans,
        'active_xmas': active_xmas,
        'total_active_xmas': total_active_xmas,
        'pending_xmas': pending_xmas,
        'total_pending_xmas': total_pending_xmas,
        'cleared_xmas': cleared_xmas,
        'total_cleared_xmas': total_cleared_xmas,
        
        # Repayments
        'repayments': repayments,
        'total_repaid': total_repaid,
        'total_regular_repaid': total_regular_repaid,
        'total_xmas_repaid': total_xmas_repaid,
        
        # Outstanding
        'outstanding_regular': outstanding_regular,
        'outstanding_xmas': outstanding_xmas,
        'total_outstanding': total_outstanding,
        
        # Transactions
        'transactions': transactions,
        'total_transactions': total_transactions,
        
        # Bereavement
        'bereavement_payments': bereavement_payments,
        'total_bereavement': total_bereavement,
        
        # Expenses
        'expenses': expenses,
        'total_expenses': total_expenses,
    }

    return render(request, 'member_report.html', context)
def sacco_reportings(request):
    if getattr(request.user, 'user_type', None) != '3' and not request.user.is_superuser:
        return redirect('access_denied')

    # ===== MEMBERS =====
    members = Profile.objects.select_related('user').all()
    member_count = members.count()
    # ✅ FIX: Use user.is_active (User model has is_active)
    active_members = members.filter(user__is_active=True).count()  # Correct way
    
    # ===== SHARES =====
    shares = CapitalShare.objects.select_related('member', 'member__user').order_by('-date_created')
    total_shares = shares.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    
    # ===== SHARE REFUNDS =====
    share_refunds = CapitalShareRefund.objects.select_related('member', 'member__user').order_by('-date_applied')
    total_share_refunds_requested = share_refunds.aggregate(Sum('amount_requested'))['amount_requested__sum'] or Decimal('0.00')
    total_share_refunds_disbursed = share_refunds.filter(status='disbursed').aggregate(Sum('amount_requested'))['amount_requested__sum'] or Decimal('0.00')
    pending_share_refunds = share_refunds.filter(status='pending').count()
    
    # ===== LOANS (Regular) =====
    loans = Loan.objects.select_related('member', 'member__user').order_by('-application_date')
    total_loans_disbursed = loans.filter(status='disbursed').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    total_loans_pending = loans.filter(status='pending').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    total_loans_approved = loans.filter(status='approved').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    total_loans_completed = loans.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    total_loans_rejected = loans.filter(status='rejected').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    
    # ===== XMAS LOANS =====
    xmas_loans = XmasLoan.objects.select_related('member', 'member__user').order_by('-application_date')
    total_xmas_disbursed = xmas_loans.filter(status='disbursed').aggregate(Sum('amount_requested'))['amount_requested__sum'] or Decimal('0.00')
    total_xmas_pending = xmas_loans.filter(status='pending').aggregate(Sum('amount_requested'))['amount_requested__sum'] or Decimal('0.00')
    total_xmas_approved = xmas_loans.filter(status='approved').aggregate(Sum('amount_requested'))['amount_requested__sum'] or Decimal('0.00')
    total_xmas_cleared = xmas_loans.filter(status='cleared').aggregate(Sum('amount_requested'))['amount_requested__sum'] or Decimal('0.00')
    
    # ===== LOAN REPAYMENTS =====
    repayments = LoanRepayment.objects.select_related('member', 'member__user').order_by('-payment_date')
    total_repaid = repayments.aggregate(Sum('amount_paid'))['amount_paid__sum'] or Decimal('0.00')
    
    # Regular loan repayments
    regular_repayments = repayments.filter(is_xmas=False)
    total_regular_repaid = regular_repayments.aggregate(Sum('amount_paid'))['amount_paid__sum'] or Decimal('0.00')
    
    # Xmas loan repayments
    xmas_repayments = repayments.filter(is_xmas=True)
    total_xmas_repaid = xmas_repayments.aggregate(Sum('amount_paid'))['amount_paid__sum'] or Decimal('0.00')
    
    # ===== OUTSTANDING BALANCES =====
    # Regular loans outstanding
    total_loan_payable = sum([loan.total_payable for loan in loans if loan.status in ['disbursed', 'approved']])
    outstanding_regular_loans = Decimal(total_loan_payable) - Decimal(total_regular_repaid)
    
    # Xmas loans outstanding
    total_xmas_payable = sum([xloan.total_payable for xloan in xmas_loans if xloan.status in ['disbursed', 'approved']])
    outstanding_xmas_loans = Decimal(total_xmas_payable) - Decimal(total_xmas_repaid)
    
    # Total outstanding
    total_outstanding = outstanding_regular_loans + outstanding_xmas_loans
    
    # ===== SAVINGS =====
    savings = MonthlyContribution.objects.select_related('member', 'member__user').order_by('-created_at')
    total_savings = savings.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    
    # ===== EXPENSES =====
    expenses = Expense.objects.select_related('recorded_by').order_by('-date_spent')
    total_expenses = expenses.aggregate(Sum('amount_spent'))['amount_spent__sum'] or Decimal('0.00')
    
    # Expenses by category
    expenses_by_type = {}
    for expense in expenses:
        expenses_by_type[expense.expense_type] = expenses_by_type.get(expense.expense_type, 0) + expense.amount_spent
    
    # ===== TRANSACTIONS =====
    transactions = Transaction.objects.select_related('member', 'member__user').order_by('-created_at')
    total_transactions = transactions.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    
    # Transactions by type
    deposits = transactions.filter(transaction_type='deposit')
    total_deposits = deposits.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    
    loan_disbursements = transactions.filter(transaction_type='loan')
    total_loan_disbursements = loan_disbursements.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    
    loan_repayments_txn = transactions.filter(transaction_type='repayment')
    total_loan_repayments_txn = loan_repayments_txn.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    
    share_transactions = transactions.filter(transaction_type='shares')
    total_share_transactions = share_transactions.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    
    # ===== BEREAVEMENT =====
    bereavement_payments = BereavementPayment.objects.select_related('member', 'member__user').order_by('-payment_date')
    total_bereavement_collected = bereavement_payments.filter(status='paid').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    
    # ===== NET POSITION =====
    # Total assets (shares + savings)
    total_assets = total_shares + total_savings
    
    # Total liabilities (outstanding loans)
    total_liabilities = total_outstanding
    
    # Net position
    net_position = total_assets - total_liabilities
    
    context = {
        # Members
        'members': members,
        'member_count': member_count,
        'active_members': active_members,
        
        # Shares
        'shares': shares,
        'total_shares': total_shares,
        
        # Share Refunds
        'share_refunds': share_refunds,
        'total_share_refunds_requested': total_share_refunds_requested,
        'total_share_refunds_disbursed': total_share_refunds_disbursed,
        'pending_share_refunds': pending_share_refunds,
        
        # Loans
        'loans': loans,
        'total_loans_disbursed': total_loans_disbursed,
        'total_loans_pending': total_loans_pending,
        'total_loans_approved': total_loans_approved,
        'total_loans_completed': total_loans_completed,
        'total_loans_rejected': total_loans_rejected,
        
        # Xmas Loans
        'xmas_loans': xmas_loans,
        'total_xmas_disbursed': total_xmas_disbursed,
        'total_xmas_pending': total_xmas_pending,
        'total_xmas_approved': total_xmas_approved,
        'total_xmas_cleared': total_xmas_cleared,
        
        # Repayments
        'repayments': repayments,
        'total_repaid': total_repaid,
        'total_regular_repaid': total_regular_repaid,
        'total_xmas_repaid': total_xmas_repaid,
        
        # Outstanding
        'outstanding_regular_loans': outstanding_regular_loans,
        'outstanding_xmas_loans': outstanding_xmas_loans,
        'total_outstanding': total_outstanding,
        
        # Savings
        'savings': savings,
        'total_savings': total_savings,
        
        # Expenses
        'expenses': expenses,
        'total_expenses': total_expenses,
        'expenses_by_type': expenses_by_type,
        
        # Transactions
        'transactions': transactions,
        'total_transactions': total_transactions,
        'total_deposits': total_deposits,
        'total_loan_disbursements': total_loan_disbursements,
        'total_loan_repayments_txn': total_loan_repayments_txn,
        'total_share_transactions': total_share_transactions,
        
        # Bereavement
        'bereavement_payments': bereavement_payments,
        'total_bereavement_collected': total_bereavement_collected,
        
        # Financial Position
        'total_assets': total_assets,
        'total_liabilities': total_liabilities,
        'net_position': net_position,
    }

    return render(request, 'sacco_reporting.html', context)
@role_required(allowed_roles=['3', '5'])  # HR Only
def Members(request):
    # Fetch all members and prefetch related loans for efficiency
    members = Profile.objects.prefetch_related('member_loans')  # ✅ works
    return render(request, 'mem.html', {'members': members})


@login_required
@role_required(allowed_roles=['1', '5'])  # HR Only
def Human_Resource(request):
    
    if getattr(request.user, 'user_type', None) != '5' and not request.user.is_superuser:
        return redirect('access_denied')

    query = request.GET.get('q')

    # =====================================================
    # BASE QUERY (SINGLE SOURCE OF TRUTH)
    # =====================================================
    base_users = Profile.objects.select_related('user')

    # =====================================================
    # FLAGGED USERS (ALWAYS FROM BASE)
    # =====================================================
    flagged_users = base_users.filter(salary_needs_review=True)

    # MAIN USERS LIST
    users = base_users

    # =====================================================
    # SEARCH FILTER
    # =====================================================
    if query:
        users = users.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(pf_number__icontains=query)
        )

    # =====================================================
    # ORDER: FLAGGED FIRST
    # =====================================================
    users = users.order_by('-salary_needs_review', 'user__first_name')

    # =====================================================
    # HR NOTIFICATIONS
    # =====================================================
    notifications = HRNotification.objects.filter(
        is_read=False
    ).select_related('member').order_by('-created_at')

    # =====================================================
    # STATS
    # =====================================================
    stats = users.aggregate(
        total_gross=Sum('gross_salary'),
        total_net=Sum('net_salary'),
        avg_gross=Avg('gross_salary')
    )

    # =====================================================
    # CONTEXT
    # =====================================================
    context = {
        'users': users,
        'flagged_users': flagged_users,
        'total_gross': stats['total_gross'] or 0,
        'total_net': stats['total_net'] or 0,
        'avg_gross': stats['avg_gross'] or 0,
        'member_count': users.count(),
        'notifications': notifications,
        'notification_count': notifications.count(),
        'flagged_count': flagged_users.count(),
    }

    return render(request, 'hr.html', context)
# views.py




from django.shortcuts import render
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from .models import Loan, LoanRepayment
import datetime as dt_module  # Avoids naming conflicts with 'datetime' class
@login_required

def performance_analysis_view(request):
    monthly_stats = {}

    # 1. Fetch Disbursed Loans
    loans = (
        Loan.objects.filter(is_disbursed=True)
        .annotate(month=TruncMonth('disbursed_at'))
        .values('month')
        .annotate(total=Sum('amount'))
    )

    # 2. Fetch Repayments
    repayments = (
        LoanRepayment.objects.annotate(month=TruncMonth('payment_date'))
        .values('month')
        .annotate(total=Sum('amount_paid'))
    )

    # 3. Merge logic for Chart.js
    for l in loans:
        if l['month']:
            m_str = l['month'].strftime("%b %Y")
            monthly_stats[m_str] = {'disbursed': float(l['total']), 'repaid': 0}

    for r in repayments:
        if r['month']:
            m_str = r['month'].strftime("%b %Y")
            total_r = float(r['total'])
            if m_str in monthly_stats:
                monthly_stats[m_str]['repaid'] = total_r
            else:
                monthly_stats[m_str] = {'disbursed': 0, 'repaid': total_r}

    # 4. Chronological Sorting (Using dt_module to prevent AttributeError)
    sorted_months = sorted(
        monthly_stats.keys(), 
        key=lambda x: dt_module.datetime.strptime(x, "%b %Y")
    )
    
    # 5. Financial Calculations
    total_disbursed = float(sum(l['total'] for l in loans) or 0)
    total_repaid = float(sum(r['total'] for r in repayments) or 0)
    
    # Calculate Recovery Rate (Capped at 100% for the UI)
    if total_disbursed > 0:
        actual_rate = (total_repaid / total_disbursed) * 100
        display_recovery = min(round(actual_rate, 1), 100.0)
        surplus = max(0, total_repaid - total_disbursed)
    else:
        display_recovery = 0
        surplus = 0

    context = {
        'labels': sorted_months,
        'loan_totals': [monthly_stats[m]['disbursed'] for m in sorted_months],
        'repayment_totals': [monthly_stats[m]['repaid'] for m in sorted_months],
        'total_disbursed': total_disbursed,
        'total_repaid': total_repaid,
        'recovery_rate': display_recovery,
        'surplus': surplus,
        'actual_yield': round((total_repaid / total_disbursed * 100), 1) if total_disbursed > 0 else 0
    }
    
    return render(request, 'analysis.html', context)
# views.py

import json
from decimal import Decimal, InvalidOperation
from django.http import JsonResponse
@login_required
@role_required(allowed_roles=['1', '2', '3', '4', '5'])  # Admin and Treasurer
def update_targets(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            profile = request.user.profile

            # Savings target
            if data.get("saving_target"):
                profile.monthly_saving_target = Decimal(data["saving_target"])

            # Share goal
            if data.get("share_goal"):
                profile.share_goal = Decimal(data["share_goal"])

            profile.save()

            return JsonResponse({
                "status": "success",
                "message": "Targets updated successfully"
            })

        except (ValueError, InvalidOperation):
            return JsonResponse({
                "status": "error",
                "message": "Invalid amount entered"
            }, status=400)

    return JsonResponse({"status": "error"}, status=405)
def update_share_goal(request):
    if request.method == "POST":
        goal_amount = request.POST.get('share_goal')
        try:
            profile = request.user.profile
            profile.share_goal = Decimal(goal_amount)
            profile.save()
            messages.success(request, f"Your new share goal is KES {profile.share_goal:,.2f}")
        except (ValueError, TypeError, Decimal.InvalidOperation):
            messages.error(request, "Invalid amount entered.")
            
    return redirect('member_dashboard')

import csv
from django.http import HttpResponse
from django.db.models import Sum
from decimal import Decimal
from django.utils import timezone
from datetime import date
from decimal import Decimal
from datetime import date
from django.db.models import Sum
from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone
import csv


# def monthly_sacco_report(request):
#     # ==========================================
#     # 1. GET MONTH & YEAR
#     # ==========================================
#     month = int(request.GET.get('month'))
#     year = int(request.GET.get('year'))
#     if not month or not year:
#         return HttpResponse("Invalid moths", status=400)

#     report_data = []

#     # Avoid N+1 queries
#     profiles = Profile.objects.select_related('user').all()

#     # ==========================================
#     # 2. LOOP THROUGH MEMBERS
#     # ==========================================
#     for profile in profiles:

#         # ==========================================
#         # SAVINGS
#         # ==========================================
#         savings_paid = MonthlyContribution.objects.filter(
#             member=profile,
#             month__month=month,
#             month__year=year
#         ).aggregate(
#             total=Sum('amount')
#         )['total'] or Decimal('0.00')

#         savings_target = profile.monthly_saving_target or Decimal('0.00')

#         savings_status = (
#             savings_paid >= savings_target
#             if savings_target > 0
#             else savings_paid > 0
#         )

#         # ==========================================
#         # SHARES
#         # ==========================================
#         shares_paid = Transaction.objects.filter(
#             member=profile,
#             transaction_type='shares',
#             created_at__month=month,
#             created_at__year=year
#         ).aggregate(
#             total=Sum('amount')
#         )['total'] or Decimal('0.00')

#         share_target = profile.share_goal or Decimal('0.00')

#         shares_status = (
#             shares_paid >= share_target
#             if share_target > 0
#             else shares_paid > 0
#         )

#         # ==========================================
#         # LOAN FUNCTION
#         # ==========================================
#         def get_loan_data(purpose_name=None, is_xmas_model=False):

#             # --------------------------------------
#             # FETCH LOANS
#             # --------------------------------------
#             if is_xmas_model:
#                 loans = XmasLoan.objects.filter(
#                     member=profile,
#                     status__in=['approved', 'disbursed']
#                 )
#             else:
#                 loans = Loan.objects.filter(
#                     member=profile,
#                     purpose__icontains=(purpose_name or ""),
#                     status__in=['approved', 'disbursed']
#                 )

#             total_expected = Decimal('0.00')
#             total_paid = Decimal('0.00')

#             # --------------------------------------
#             # LOOP THROUGH ALL LOANS
#             # --------------------------------------
#             for loan in loans:

#                 expected = loan.monthly_installment or Decimal('0.00')

#                 repayment_filter = {
#                     'payment_date__month': month,
#                     'payment_date__year': year,
#                 }

#                 if is_xmas_model:
#                     repayment_filter['member'] = profile
#                     repayment_filter['is_xmas'] = True
#                 else:
#                     repayment_filter['loan'] = loan

#                 paid = LoanRepayment.objects.filter(
#                     **repayment_filter
#                 ).aggregate(
#                     total=Sum('amount_paid')
#                 )['total'] or Decimal('0.00')

#                 total_expected += expected
#                 total_paid += paid

#             status = (
#                 total_paid >= total_expected
#                 if total_expected > 0
#                 else False
#             )

#             return total_expected, total_paid, status

#         # ==========================================
#         # LOAN TYPES
#         # ==========================================
#         norm_exp, norm_paid, norm_status = get_loan_data('normal')

#         xmas_exp, xmas_paid, xmas_status = get_loan_data(
#             is_xmas_model=True
#         )

#         sch_exp, sch_paid, sch_status = get_loan_data('school')

#         emg_exp, emg_paid, emg_status = get_loan_data('emergency')

#         # ==========================================
#         # BUILD ROW
#         # ==========================================
#         row = {
#             'name': profile.user.get_full_name() or profile.user.username,
#             'pf': profile.pf_number,

#             # SAVINGS
#             'savings_paid': savings_paid,
#             'savings_target': savings_target,
#             'savings_status': savings_status,

#             # SHARES
#             'shares_paid': shares_paid,
#             'shares_target': share_target,
#             'shares_status': shares_status,

#             # NORMAL LOAN
#             'normal_loan': norm_exp,
#             'normal_paid': norm_paid,
#             'normal_status': norm_status,

#             # XMAS LOAN
#             'xmas_loan': xmas_exp,
#             'xmas_paid': xmas_paid,
#             'xmas_status': xmas_status,

#             # SCHOOL FEES
#             'school_fees': sch_exp,
#             'school_paid': sch_paid,
#             'school_status': sch_status,

#             # EMERGENCY
#             'emergency': emg_exp,
#             'emergency_paid': emg_paid,
#             'emergency_status': emg_status,

#             # TOTAL
#             'total_actual_paid': (
#                 savings_paid +
#                 shares_paid +
#                 norm_paid +
#                 xmas_paid +
#                 sch_paid +
#                 emg_paid
#             )
#         }

#         report_data.append(row)

#     # ==========================================
#     # 3. CSV EXPORT
#     # ==========================================
#     if 'export' in request.GET:

#         response = HttpResponse(content_type='text/csv')

#         response['Content-Disposition'] = (
#             f'attachment; filename="SACCO_Report_{month}_{year}.csv"'
#         )

#         writer = csv.writer(response)

#         writer.writerow([
#             'Member Name',
#             'PF Number',
#             'Xmass Contri',
#             'Normal Shares',
#             'Normal Loans',
#             'Quick Loans',
#             'School Fees',
#             'Emergency'
#         ])

#         for r in report_data:

#             writer.writerow([
#                 r['name'],
#                 r['pf'],

#                 0 if r['savings_status'] else r['savings_target'],

#                 0 if r['shares_status'] else r['shares_target'],

#                 0 if r['normal_status'] else r['normal_loan'],

#                 0 if r['xmas_status'] else r['xmas_loan'],

#                 0 if r['school_status'] else r['school_fees'],

#                 0 if r['emergency_status'] else r['emergency'],
#             ])

#         return response

#     # ==========================================
#     # 4. RENDER TEMPLATE
#     # ==========================================
#     context = {
#         'report_data': report_data,
#         'month': month,
#         'year': year,
#         'years': range(2023, 2030),
#         'months_choices': [
#             (i, date(2000, i, 1).strftime('%b'))
#             for i in range(1, 13)
#         ],
#     }

#     return render(
#         request,
#         'monthly_report.html',
#         context
#     )
from decimal import Decimal
from datetime import date
import csv

from django.db.models import Sum
from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone

from .models import (
    Profile,
    MonthlyContribution,
    Loan,
    XmasLoan,
    LoanRepayment,
    CapitalShare,
)
from decimal import Decimal, ROUND_CEILING
from django.utils import timezone
from django.http import HttpResponse
import csv

def round_up(value):
    return value.quantize(Decimal('1'), rounding=ROUND_CEILING)
@login_required


@role_required(allowed_roles=['1', '2', '3'])
def monthly_sacco_report(request):
    current_date = timezone.now()
    month = request.GET.get('month')
    year = request.GET.get('year')

    if not month:
        month = current_date.month
    if not year:
        year = current_date.year

    try:
        month = int(month)
        year = int(year)
    except ValueError:
        return HttpResponse("Invalid month or year", status=400)

    report_data = []
    profiles = Profile.objects.select_related('user').all()

    def round_up(value):
        return value.quantize(Decimal('1'), rounding=ROUND_CEILING)

    for profile in profiles:
        # ---------- Savings & Shares (unchanged) ----------
        savings_paid = MonthlyContribution.objects.filter(
            member=profile,
            month__month=month,
            month__year=year
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        savings_target = profile.monthly_saving_target or Decimal('0.00')
        savings_status = savings_paid >= savings_target if savings_target > 0 else savings_paid > 0
        savings_due = round_up(max(Decimal('0.00'), savings_target - savings_paid))
        savings_csv_value = Decimal('0.00') if savings_status else savings_due

        shares_paid = CapitalShare.objects.filter(
            member=profile,
            month__month=month,
            month__year=year
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        share_target = profile.share_goal or Decimal('0.00')
        shares_status = shares_paid >= share_target if share_target > 0 else shares_paid > 0
        shares_due = round_up(max(Decimal('0.00'), share_target - shares_paid))
        shares_csv_value = Decimal('0.00') if shares_status else shares_due

        # ---------- Loans (unchanged) ----------
        def get_loan_data(purpose=None, is_xmas=False):
            if is_xmas:
                loans = XmasLoan.objects.filter(
                    member=profile,
                    status__in=['approved', 'disbursed']
                )
            else:
                loans = Loan.objects.filter(
                    member=profile,
                    purpose__icontains=(purpose or ""),
                    status__in=['approved', 'disbursed']
                )

            total_expected = Decimal('0.00')
            total_paid = Decimal('0.00')

            for loan in loans:
                expected = loan.monthly_installment or Decimal('0.00')
                filters = {'payment_date__month': month, 'payment_date__year': year}
                if is_xmas:
                    filters['member'] = profile
                    filters['is_xmas'] = True
                else:
                    filters['loan'] = loan

                paid = LoanRepayment.objects.filter(**filters).aggregate(
                    total=Sum('amount_paid')
                )['total'] or Decimal('0.00')

                total_expected += expected
                total_paid += paid

            status = total_paid >= total_expected if total_expected > 0 else False
            due = round_up(max(Decimal('0.00'), total_expected - total_paid))
            csv_value = Decimal('0.00') if status else due
            return total_expected, total_paid, status, due, csv_value

        norm_exp, norm_paid, norm_status, norm_due, norm_csv = get_loan_data('normal')
        xmas_exp, xmas_paid, xmas_status, xmas_due, xmas_csv = get_loan_data(is_xmas=True)
        sch_exp, sch_paid, sch_status, sch_due, sch_csv = get_loan_data('school')
        emg_exp, emg_paid, emg_status, emg_due, emg_csv = get_loan_data('emergency')

        # ---------- BEREAVEMENT (unchanged) ----------
        ber_owed = Decimal('0.00')
        ber_paid = Decimal('0.00')
        ber_ann_count = 0

        active_anns = BereavementAnnouncement.objects.filter(
            is_active=True,
            is_approved=True
        )

        for ann in active_anns:
            end_month = ann.start_month + ann.repayment_months - 1
            end_year = ann.start_year
            while end_month > 12:
                end_month -= 12
                end_year += 1

            if (ann.start_year < year) or (ann.start_year == year and ann.start_month <= month):
                if (end_year > year) or (end_year == year and end_month >= month):
                    if ann.member != profile:
                        ber_ann_count += 1
                        payment = BereavementPayment.objects.filter(
                            member=profile,
                            announcement=ann,
                            payment_month=month,
                            payment_year=year,
                            status='paid'
                        ).first()
                        if payment:
                            ber_paid += payment.amount
                        else:
                            ber_owed += ann.monthly_amount_per_member

        if ber_owed == 0:
            ber_status = True
            ber_due = Decimal('0.00')
        else:
            if ber_paid >= ber_owed:
                ber_status = True
                ber_due = Decimal('0.00')
            else:
                ber_status = False
                ber_due = ber_owed - ber_paid
        ber_csv_value = Decimal('0.00') if ber_status else ber_due

        # ---------- RETIREMENT (new) ----------
        ret_owed = Decimal('0.00')
        ret_paid = Decimal('0.00')
        ret_ann_count = 0

        active_ret_anns = RetirementAnnouncement.objects.filter(
            is_active=True,
            is_approved=True
        )

        for ann in active_ret_anns:
            end_month = ann.start_month + ann.repayment_months - 1
            end_year = ann.start_year
            while end_month > 12:
                end_month -= 12
                end_year += 1

            if (ann.start_year < year) or (ann.start_year == year and ann.start_month <= month):
                if (end_year > year) or (end_year == year and end_month >= month):
                    if ann.member != profile:   # retiree is exempt
                        ret_ann_count += 1
                        payment = RetirementPayment.objects.filter(
                            member=profile,
                            announcement=ann,
                            payment_month=month,
                            payment_year=year,
                            status='paid'
                        ).first()
                        if payment:
                            ret_paid += payment.amount
                        else:
                            ret_owed += ann.monthly_amount_per_member

        if ret_owed == 0:
            ret_status = True
            ret_due = Decimal('0.00')
        else:
            if ret_paid >= ret_owed:
                ret_status = True
                ret_due = Decimal('0.00')
            else:
                ret_status = False
                ret_due = ret_owed - ret_paid
        ret_csv_value = Decimal('0.00') if ret_status else ret_due

        # ---------- TOTALS (include retirement) ----------
        total_actual_paid = (
            savings_paid + shares_paid +
            norm_paid + xmas_paid +
            sch_paid + emg_paid +
            ber_paid + ret_paid
        )

        total_due = (
            savings_due + shares_due +
            norm_due + xmas_due +
            sch_due + emg_due +
            ber_due + ret_due
        )

        total_csv_value = (
            savings_csv_value + shares_csv_value +
            norm_csv + xmas_csv +
            sch_csv + emg_csv +
            ber_csv_value + ret_csv_value
        )

        report_data.append({
            'name': profile.user.get_full_name() or profile.user.username,
            'pf': profile.pf_number,

            'savings_paid': savings_paid,
            'savings_target': savings_target,
            'savings_status': savings_status,
            'savings_due': savings_due,
            'savings_csv': savings_csv_value,

            'shares_paid': shares_paid,
            'shares_target': share_target,
            'shares_status': shares_status,
            'shares_due': shares_due,
            'shares_csv': shares_csv_value,

            'normal_paid': norm_paid,
            'normal_status': norm_status,
            'normal_due': norm_due,
            'normal_csv': norm_csv,

            'xmas_paid': xmas_paid,
            'xmas_status': xmas_status,
            'xmas_due': xmas_due,
            'xmas_csv': xmas_csv,

            'school_paid': sch_paid,
            'school_status': sch_status,
            'school_due': sch_due,
            'school_csv': sch_csv,

            'emergency_paid': emg_paid,
            'emergency_status': emg_status,
            'emergency_due': emg_due,
            'emergency_csv': emg_csv,

            'bereavement_paid': ber_paid,
            'bereavement_owed': ber_owed,
            'bereavement_ann_count': ber_ann_count,
            'bereavement_status': ber_status,
            'bereavement_due': ber_due,
            'bereavement_csv': ber_csv_value,

            'retirement_paid': ret_paid,
            'retirement_owed': ret_owed,
            'retirement_ann_count': ret_ann_count,
            'retirement_status': ret_status,
            'retirement_due': ret_due,
            'retirement_csv': ret_csv_value,

            'total_actual_paid': total_actual_paid,
            'total_due': total_due,
            'total_csv': total_csv_value,
        })

    # ---------- CSV Export (update to include retirement) ----------
    if 'export' in request.GET:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="sacco_report_{month}_{year}.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'Member', 'PF',
            'Savings Paid', 'Savings Target', 'Savings Status', 'Savings Due',
            'Shares Paid', 'Shares Target', 'Shares Status', 'Shares Due',
            'Standard Loan Paid', 'Standard Loan Status', 'Standard Loan Due',
            'Holiday Loan Paid', 'Holiday Loan Status', 'Holiday Loan Due',
            'School Loan Paid', 'School Loan Status', 'School Loan Due',
            'Emergency Loan Paid', 'Emergency Loan Status', 'Emergency Loan Due',
            'Bereavement Paid', 'Bereavement Owed', 'Bereavement Count', 'Bereavement Status', 'Bereavement Due',
            'Retirement Paid', 'Retirement Owed', 'Retirement Count', 'Retirement Status', 'Retirement Due',
            'Total Paid', 'Total Due'
        ])
        for row in report_data:
            writer.writerow([
                row['name'], row['pf'],
                row['savings_paid'], row['savings_target'], row['savings_status'], row['savings_due'],
                row['shares_paid'], row['shares_target'], row['shares_status'], row['shares_due'],
                row['normal_paid'], row['normal_status'], row['normal_due'],
                row['xmas_paid'], row['xmas_status'], row['xmas_due'],
                row['school_paid'], row['school_status'], row['school_due'],
                row['emergency_paid'], row['emergency_status'], row['emergency_due'],
                row['bereavement_paid'], row['bereavement_owed'], row['bereavement_ann_count'],
                row['bereavement_status'], row['bereavement_due'],
                row['retirement_paid'], row['retirement_owed'], row['retirement_ann_count'],
                row['retirement_status'], row['retirement_due'],
                row['total_actual_paid'], row['total_due']
            ])
        return response

    return render(request, 'monthly_report.html', {
        'report_data': report_data,
        'month': month,
        'year': year,
        'years': range(2023, 2035),
        'months_choices': [
            (i, date(2000, i, 1).strftime('%b'))
            for i in range(1, 13)
        ],
    })
# ===== CSV export helper (keep your existing implementation) =====
def export_sacco_report_csv(report_data, month, year):
    import csv
    from django.http import HttpResponse

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="sacco_report_{month}_{year}.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Member', 'PF',
        'Savings Paid', 'Savings Target', 'Savings Status', 'Savings Due',
        'Shares Paid', 'Shares Target', 'Shares Status', 'Shares Due',
        'Standard Loan Paid', 'Standard Loan Status', 'Standard Loan Due',
        'Holiday Loan Paid', 'Holiday Loan Status', 'Holiday Loan Due',
        'School Loan Paid', 'School Loan Status', 'School Loan Due',
        'Emergency Loan Paid', 'Emergency Loan Status', 'Emergency Loan Due',
        'Bereavement Paid', 'Bereavement Owed', 'Bereavement Count', 'Bereavement Status', 'Bereavement Due',
        'Total Paid', 'Total Due'
    ])

    for row in report_data:
        writer.writerow([
            row['name'], row['pf'],
            row['savings_paid'], row['savings_target'], row['savings_status'], row['savings_due'],
            row['shares_paid'], row['shares_target'], row['shares_status'], row['shares_due'],
            row['normal_paid'], row['normal_status'], row['normal_due'],
            row['xmas_paid'], row['xmas_status'], row['xmas_due'],
            row['school_paid'], row['school_status'], row['school_due'],
            row['emergency_paid'], row['emergency_status'], row['emergency_due'],
            row['bereavement_paid'], row['bereavement_owed'], row['bereavement_ann_count'],
            row['bereavement_status'], row['bereavement_due'],
            row['total_actual_paid'], row['total_due']
        ])

    return response
# def monthly_sacco_report(request):
#     current_date = timezone.now()
#     month = request.GET.get('month')
#     year = request.GET.get('year')

#     if not month:
#         month = current_date.month
#     if not year:
#         year = current_date.year

#     try:
#         month = int(month)
#         year = int(year)
#     except ValueError:
#         return HttpResponse("Invalid month or year", status=400)

#     report_data = []
#     profiles = Profile.objects.select_related('user').all()

#     def round_up(value):
#         return value.quantize(Decimal('1'), rounding=ROUND_CEILING)

#     for profile in profiles:
#         # ===================== SAVINGS =====================
#         savings_paid = MonthlyContribution.objects.filter(
#             member=profile,
#             month__month=month,
#             month__year=year
#         ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

#         savings_target = profile.monthly_saving_target or Decimal('0.00')
#         savings_status = savings_paid >= savings_target if savings_target > 0 else savings_paid > 0
#         savings_due = round_up(max(Decimal('0.00'), savings_target - savings_paid))
#         savings_csv_value = Decimal('0.00') if savings_status else savings_due

#         # ===================== SHARES =====================
#         shares_paid = CapitalShare.objects.filter(
#             member=profile,
#             month__month=month,
#             month__year=year
#         ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

#         share_target = profile.share_goal or Decimal('0.00')
#         shares_status = shares_paid >= share_target if share_target > 0 else shares_paid > 0
#         shares_due = round_up(max(Decimal('0.00'), share_target - shares_paid))
#         shares_csv_value = Decimal('0.00') if shares_status else shares_due

#         # ===================== LOANS =====================
#         def get_loan_data(purpose=None, is_xmas=False):
#             if is_xmas:
#                 loans = XmasLoan.objects.filter(
#                     member=profile,
#                     status__in=['approved', 'disbursed']
#                 )
#             else:
#                 loans = Loan.objects.filter(
#                     member=profile,
#                     purpose__icontains=(purpose or ""),
#                     status__in=['approved', 'disbursed']
#                 )

#             total_expected = Decimal('0.00')
#             total_paid = Decimal('0.00')

#             for loan in loans:
#                 expected = loan.monthly_installment or Decimal('0.00')
#                 filters = {'payment_date__month': month, 'payment_date__year': year}
#                 if is_xmas:
#                     filters['member'] = profile
#                     filters['is_xmas'] = True
#                 else:
#                     filters['loan'] = loan

#                 paid = LoanRepayment.objects.filter(**filters).aggregate(
#                     total=Sum('amount_paid')
#                 )['total'] or Decimal('0.00')

#                 total_expected += expected
#                 total_paid += paid

#             status = total_paid >= total_expected if total_expected > 0 else False
#             due = round_up(max(Decimal('0.00'), total_expected - total_paid))
#             csv_value = Decimal('0.00') if status else due
#             return total_expected, total_paid, status, due, csv_value

#         norm_exp, norm_paid, norm_status, norm_due, norm_csv = get_loan_data('normal')
#         xmas_exp, xmas_paid, xmas_status, xmas_due, xmas_csv = get_loan_data(is_xmas=True)
#         sch_exp, sch_paid, sch_status, sch_due, sch_csv = get_loan_data('school')
#         emg_exp, emg_paid, emg_status, emg_due, emg_csv = get_loan_data('emergency')

#         # ===================== BEREAVEMENT (MONTHLY OBLIGATION) =====================
#         ber_owed = Decimal('0.00')
#         ber_paid = Decimal('0.00')

#         # Get all active, approved announcements
#         active_anns = BereavementAnnouncement.objects.filter(
#             is_active=True,
#             is_approved=True
#         )

#         for ann in active_anns:
#             # Compute the end month/year of the repayment period
#             end_month = ann.start_month + ann.repayment_months - 1
#             end_year = ann.start_year
#             while end_month > 12:
#                 end_month -= 12
#                 end_year += 1

#             # Check if selected (month, year) falls within [start, end]
#             if (ann.start_year < year) or (ann.start_year == year and ann.start_month <= month):
#                 if (end_year > year) or (end_year == year and end_month >= month):
#                     # This announcement is active in this month
#                     # Exempt the bereaved member
#                     if ann.member != profile:
#                         # Check if the member has already paid this month's instalment
#                         payment = BereavementPayment.objects.filter(
#                             member=profile,
#                             announcement=ann,
#                             payment_month=month,
#                             payment_year=year,
#                             status='paid'
#                         ).first()

#                         if payment:
#                             ber_paid += payment.amount
#                         else:
#                             ber_owed += ann.monthly_amount_per_member

#         # Determine status and due
#         if ber_owed == 0:
#             ber_status = True
#             ber_due = Decimal('0.00')
#         else:
#             if ber_paid >= ber_owed:
#                 ber_status = True
#                 ber_due = Decimal('0.00')
#             else:
#                 ber_status = False
#                 ber_due = ber_owed - ber_paid

#         ber_csv_value = Decimal('0.00') if ber_status else ber_due

#         # ===================== TOTALS =====================
#         total_actual_paid = (
#             savings_paid + shares_paid +
#             norm_paid + xmas_paid +
#             sch_paid + emg_paid +
#             ber_paid
#         )

#         total_due = (
#             savings_due + shares_due +
#             norm_due + xmas_due +
#             sch_due + emg_due +
#             ber_due
#         )

#         total_csv_value = (
#             savings_csv_value + shares_csv_value +
#             norm_csv + xmas_csv +
#             sch_csv + emg_csv +
#             ber_csv_value
#         )

#         report_data.append({
#             'name': profile.user.get_full_name() or profile.user.username,
#             'pf': profile.pf_number,

#             'savings_paid': savings_paid,
#             'savings_target': savings_target,
#             'savings_status': savings_status,
#             'savings_due': savings_due,
#             'savings_csv': savings_csv_value,

#             'shares_paid': shares_paid,
#             'shares_target': share_target,
#             'shares_status': shares_status,
#             'shares_due': shares_due,
#             'shares_csv': shares_csv_value,

#             'normal_paid': norm_paid,
#             'normal_status': norm_status,
#             'normal_due': norm_due,
#             'normal_csv': norm_csv,

#             'xmas_paid': xmas_paid,
#             'xmas_status': xmas_status,
#             'xmas_due': xmas_due,
#             'xmas_csv': xmas_csv,

#             'school_paid': sch_paid,
#             'school_status': sch_status,
#             'school_due': sch_due,
#             'school_csv': sch_csv,

#             'emergency_paid': emg_paid,
#             'emergency_status': emg_status,
#             'emergency_due': emg_due,
#             'emergency_csv': emg_csv,

#             'bereavement_paid': ber_paid,
#             'bereavement_owed': ber_owed,        # NEW: total monthly obligation
#             'bereavement_status': ber_status,
#             'bereavement_due': ber_due,
#             'bereavement_csv': ber_csv_value,

#             'total_actual_paid': total_actual_paid,
#             'total_due': total_due,
#             'total_csv': total_csv_value,
#         })

#     # ===================== CSV EXPORT =====================
#     if 'export' in request.GET:
#         return export_sacco_report_csv(report_data, month, year)

#     return render(request, 'monthly_report.html', {
#         'report_data': report_data,
#         'month': month,
#         'year': year,
#         'years': range(2023, 2035),
#         'months_choices': [
#             (i, date(2000, i, 1).strftime('%b'))
#             for i in range(1, 13)
#         ],
#     })
# def export_sacco_report_csv(report_data, month, year):
#     response = HttpResponse(content_type='text/csv')
#     response['Content-Disposition'] = f'attachment; filename="WELFARE_Report_{month}_{year}.csv"'
    
#     writer = csv.writer(response)
    
#     # Header - SHOW ONLY DUE AMOUNTS (0 if paid)
#     writer.writerow([
#         'Member Name', 
#         'PF Number',
#         'Savings Due',
#         'Shares Due',
#         'Normal Loan Due',
#         'Xmas Loan Due',
#         'School Fees Due',
#         'Emergency Due',
#         'Bereavement Due',
#         'Total Due'
#     ])
    
#     # Data rows - ONLY show amounts that are due (0 if paid)
#     for row in report_data:
#         writer.writerow([
#             row['name'], 
#             row['pf'],
#             float(row['savings_csv']),      # 0 if paid, else due amount
#             float(row['shares_csv']),       # 0 if paid, else due amount
#             float(row['normal_csv']),       # 0 if paid, else due amount
#             float(row['xmas_csv']),         # 0 if paid, else due amount
#             float(row['school_csv']),       # 0 if paid, else due amount
#             float(row['emergency_csv']),    # 0 if paid, else due amount
#             float(row['bereavement_csv']),  # 0 if paid, else due amount
#             float(row['total_csv']),        # Total due amount
#         ])
    
#     return response
def financial_ledger_view(request):
    user_profile = request.user.profile
    
    # --- MEMBER SPECIFIC DATA ---
    monthly_savings = MonthlyContribution.objects.filter(member=user_profile)
    capital_shares = CapitalShare.objects.filter(member=user_profile)
    
    total_savings = (monthly_savings.aggregate(Sum('amount'))['amount__sum'] or 0) + \
                    (capital_shares.aggregate(Sum('amount'))['amount__sum'] or 0)

    # Combined Ledger (Historical list of everything the member did)
    ledger_entries = []
    for s in monthly_savings:
        ledger_entries.append({'date': s.created_at, 'type': 'Monthly Saving', 'amount': s.amount, 'month': s.month})
    for c in capital_shares:
        ledger_entries.append({'date': c.date_created, 'type': 'Capital Share', 'amount': c.amount, 'month': c.month})
    
    ledger_entries = sorted(ledger_entries, key=lambda x: x['date'], reverse=True)

    repayments = LoanRepayment.objects.filter(member=user_profile).order_by('-payment_date')
    total_repaid = repayments.aggregate(Sum('amount_paid'))['amount_paid__sum'] or Decimal('0.00')
    
    # Active Debt Calculation
    active_loans = Loan.objects.filter(member=user_profile, status='disbursed').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    active_xmas = XmasLoan.objects.filter(member=user_profile, is_disbursed=True).aggregate(Sum('amount_requested'))['amount_requested__sum'] or Decimal('0.00')
    current_loan_balance = (active_loans + active_xmas) - total_repaid

    # --- TREASURER CASH FLOW LOGIC (Global Overview) ---
    cashflow_stats = {}
    if request.user.user_type in ['1', '2', '3']:
        # INFLOWS
        in_savings = MonthlyContribution.objects.aggregate(Sum('amount'))['amount__sum'] or 0
        in_shares = CapitalShare.objects.aggregate(Sum('amount'))['amount__sum'] or 0
        in_repayments = LoanRepayment.objects.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
        in_reg_fees = RegistrationFee.objects.filter(paid=True).aggregate(Sum('amount'))['amount__sum'] or 0
        
        total_inflow = in_savings + in_shares + in_repayments + in_reg_fees

        # OUTFLOWS
        out_loans = Loan.objects.filter(status='disbursed').aggregate(Sum('amount'))['amount__sum'] or 0
        out_xmas = XmasLoan.objects.filter(status='disbursed').aggregate(Sum('amount_requested'))['amount_requested__sum'] or 0
        out_expenses = Expense.objects.aggregate(Sum('amount_spent'))['amount_spent__sum'] or 0
        out_refunds = CapitalShareRefund.objects.filter(status='disbursed').aggregate(Sum('amount_requested'))['amount_requested__sum'] or 0
        
        total_outflow = out_loans + out_xmas + out_expenses + out_refunds

        cashflow_stats = {
            'total_in': total_inflow,
            'total_out': total_outflow,
            'net_cash': total_inflow - total_outflow,
            'expense_ratio': (out_expenses / total_inflow * 100) if total_inflow > 0 else 0,
            'breakdown': {
                'expenses': out_expenses,
                'refunds': out_refunds,
                'repayments': in_repayments
            }
        }

    context = {
        'total_savings': total_savings,
        'ledger': ledger_entries,
        'current_balance': current_loan_balance,
        'total_repaid': total_repaid,
        'history': repayments,
        'cashflow_stats': cashflow_stats,
    }
    return render(request, 'financial_report.html', context)


def get_daily_financial_summary():
    """Calculates total cash flow for the current day."""
    today = timezone.now().date()
    
    # Sum of all money coming IN
    inflow = Transaction.objects.filter(
        created_at__date=today,
        transaction_type__in=['deposit', 'repayment', 'shares']
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Sum of all money going OUT
    outflow = Transaction.objects.filter(
        created_at__date=today,
        transaction_type='loan'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    return {
        'inflow': inflow,
        'outflow': outflow,
        'net_flow': inflow - outflow
    }
from datetime import datetime, date

# ... (inside your sacco_financial_ledger_view) ...

# ---------------------------------------------------------
# 3. SORTING & TOTALS
# ---------------------------------------------------------

# Helper function to ensure we are comparing apples to apples (date vs date)
from django.db.models import Sum
from datetime import date, datetime
import datetime as dt_module  # The classes
import datetime as dt_module # Rename the module import
from datetime import date, datetime

def normalize_date(val):
    """
    Bulletproof date normalization for Python 3.14.
    Returns a datetime.date object for sorting.
    """
    if val is None:
        return date.min

    # 1. If it's already a date but NOT a datetime
    if type(val) is date:
        return val

    # 2. If it has a .date() method (works for datetime objects)
    if hasattr(val, 'date'):
        return val.date()
    
    # 3. If it's a string, try to parse it
    if isinstance(val, str):
        try:
            # Handle standard Django/ISO format
            return datetime.strptime(val[:10], '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return date.min

    # 4. Fallback
    return date.min


def sacco_financial_ledger_view(request):
    # ---------------------------------------------------------
    # 1. FETCH ALL FINANCIAL DATA (ENTIRE SACCO)
    # ---------------------------------------------------------
    # Savings & Shares
    monthly_savings = MonthlyContribution.objects.all().select_related('member__user')
    capital_shares = CapitalShare.objects.all().select_related('member__user')
    
    # Loans (Disbursed only)
    loans = Loan.objects.filter(status='disbursed').select_related('member__user')
    xmas_loans = XmasLoan.objects.filter(is_disbursed=True).select_related('member__user')
    
    # Repayments (From your updated Schedule model)
    paid_schedules = LoanRepaymentSchedule.objects.filter(is_paid=True).select_related(
        'loan__member__user', 'xmas_loan__member__user'
    )

    ledger_entries = []

    # ---------------------------------------------------------
    # 2. MAP DATA TO LEDGER COLUMNS
    # ---------------------------------------------------------
    # Process Savings/Shares (Column: RCVD)
    for s in monthly_savings:
        ledger_entries.append({
            'date': s.created_at,
            'member': s.member.user.get_full_name(),
            'acc': s.member.membership_number,
            'type': 'Monthly Contribution',
            'share_rcvd': s.amount,
            'loan_amt': 0, 'loan_repaid': 0, 'int_paid': 0
        })

    for c in capital_shares:
        ledger_entries.append({
            'date': c.date_created,
            'member': c.member.user.get_full_name(),
            'acc': c.member.membership_number,
            'type': 'Capital Share',
            'share_rcvd': c.amount,
            'loan_amt': 0, 'loan_repaid': 0, 'int_paid': 0
        })

    # Process Disbursements (Column: LOANED)
    for l in loans:
        ledger_entries.append({
            'date': l.disbursed_at,
            'member': l.member.user.get_full_name(),
            'acc': l.member.membership_number,
            'type': 'Loan Disbursed',
            'share_rcvd': 0,
            'loan_amt': l.amount,
            'loan_repaid': 0, 'int_paid': 0
        })

    for xl in xmas_loans:
        ledger_entries.append({
            'date': xl.disbursement_date,
            'member': xl.member.user.get_full_name(),
            'acc': xl.member.membership_number,
            'type': 'Xmas Loan Disbursed',
            'share_rcvd': 0,
            'loan_amt': xl.amount_requested,
            'loan_repaid': 0, 'int_paid': 0
        })

    # Process Repayments (Columns: REPAID & INTEREST PAID)
    for sched in paid_schedules:
        # Determine the correct member based on loan type
        member_obj = sched.xmas_loan.member if sched.is_xmas else sched.loan.member
        
        ledger_entries.append({
            'date': sched.date_paid or sched.due_date,
            'member': member_obj.user.get_full_name(),
            'acc': member_obj.membership_number,
            'type': f"Repayment (Inst. {sched.installment_number})",
            'share_rcvd': 0,
            'loan_amt': 0,
            'loan_repaid': sched.amount_due, # Principal part
            #'int_paid': sched.interest_amount,     # Interest part
        })

    # ---------------------------------------------------------
    # 3. SORTING & TOTALS
    # ---------------------------------------------------------
    # Sort entire SACCO history by newest first
    ledger_entries.sort(
        key=lambda x: normalize_date(x.get('date')), 
        reverse=True
    )

    # Calculate Summary Totals
    total_savings = (monthly_savings.aggregate(Sum('amount'))['amount__sum'] or 0) + \
                    (capital_shares.aggregate(Sum('amount'))['amount__sum'] or 0)
    
    total_out = (loans.aggregate(Sum('amount'))['amount__sum'] or 0) + \
                (xmas_loans.aggregate(Sum('amount_requested'))['amount_requested__sum'] or 0)
                
    total_repaid = paid_schedules.aggregate(Sum('amount_due'))['amount_due__sum'] or 0
   # total_interest = paid_schedules.aggregate(Sum('interest_amount'))['interest_amount__sum'] or 0

    context = {
        'ledger': ledger_entries,
        'total_savings': total_savings,
        'total_out': total_out,
        'total_repaid': total_repaid,
        # 'total_interest': total_interest,
        'liquidity': (total_savings + total_repaid ) - total_out
    }

    return render(request, 'sacco_financial_report.html', context)
def treasurer(request):
    # ... other logic ...
    
    # Get the summary from your function
    summary = get_daily_financial_summary()
    
    # Fetch the last 10 transactions for the live feed
    recent_transactions = Transaction.objects.all().order_by('-created_at')[:10]
    
    return render(request, 'daily.html', {
        'summary': summary,
        'transactions': recent_transactions
    })
@login_required
@role_required(allowed_roles=['3']) # Treasurer
def treasurer_edit_loan_amount(request, loan_id):
    loan = get_object_or_404(Loan, id=loan_id)
    
    # Only allow editing if the loan isn't disbursed yet
    if loan.status == 'disbursed':
        messages.error(request, "Cannot edit an already disbursed loan.")
        return redirect('treasurer_dashboard')

    if request.method == "POST":
        new_amount = Decimal(request.POST.get('amount'))
        
        # ===== FIX: Update the amount and recalculate =====
        loan.amount = new_amount
        
        # Force recalculation of interest and insurance to 0
        loan.interest = Decimal('0.00')
        loan.insurance = Decimal('0.00')
        loan.interest_rate = Decimal('0.00')
        
        # Ensure duration doesn't exceed 24 months
        if loan.duration_months > 24:
            loan.duration_months = 24
        
        loan.save()
        
        messages.success(request, f"Loan amount adjusted to KES {new_amount:,.2f}")
        return redirect('treasurer_dashboard')

    return render(request, 'treasurer_edit_loan.html', {'loan': loan})


from .balance import BalanceSheetService
from django.http import JsonResponse
from .models import Transaction, MonthlyContribution, Loan, LoanRepayment
from django.http import JsonResponse
from django.utils import timezone
from decimal import Decimal
def get_note_details(request, note_id):
    year = int(request.GET.get('year', timezone.now().year))
    data = []

    # -------------------------
    # NOTE 7: CASH & BANK
    # -------------------------
    if note_id == "7":
        records = Transaction.objects.filter(
            created_at__year=year
        ).select_related('member').order_by('-created_at')

        for r in records:
            data.append({
                'date': r.created_at.strftime('%Y-%m-%d'),
                'desc': f"{r.get_transaction_type_display()} - {r.member}",
                'amount': float(r.amount),
                'type': 'in' if r.transaction_type in ['deposit', 'repayment', 'shares'] else 'out'
            })

    # -------------------------
    # NOTE 12: MEMBERS DEPOSITS
    # -------------------------
    elif note_id == "12":
        records = MonthlyContribution.objects.filter(
            month__year=year
        ).select_related('member').order_by('-month')

        for r in records:
            data.append({
                'date': r.month.strftime('%b %Y'),
                'desc': f"Monthly Contribution - {r.member}",
                'amount': float(r.amount or 0),
                'type': 'in'
            })

    # -------------------------
    # NOTE 9: LOANS TO MEMBERS
    # -------------------------
    elif note_id == "9":
        records = Loan.objects.filter(
            application_date__year=year,
            status__in=['approved', 'disbursed']
        ).select_related('member')

        for r in records:
            data.append({
                'date': r.application_date.strftime('%Y-%m-%d'),
                'desc': f"Loan to {r.member} ({r.purpose})",
                'amount': float(r.amount),
                'type': 'out'
            })

    # -------------------------
    # NOTE 13: ACCRUED EXPENSES (UPDATED - Includes Bereavement)
    # -------------------------
    elif note_id == "13":
        # ===== 1. Regular Expenses =====
        expense_records = Expense.objects.filter(
            date_spent__year=year
        ).select_related('recorded_by').order_by('-date_spent')

        for r in expense_records:
            data.append({
                'date': r.date_spent.strftime('%Y-%m-%d'),
                'desc': f"{r.get_expense_type_display()} - {r.description or ''}",
                'amount': float(r.amount_spent),
                'type': 'out'
            })

        # ===== 2. Bereavement Payments (Accrued Expenses) =====
        bereavement_records = BereavementPayment.objects.filter(
            payment_year=year,
            status='paid'
        ).select_related('member').order_by('-payment_date')

        for r in bereavement_records:
            data.append({
                'date': r.payment_date.strftime('%Y-%m-%d'),
                'desc': f"Bereavement Payout - {r.member}",
                'amount': float(r.amount),
                'type': 'out'
            })

    # -------------------------
    # NOTE 14: INTEREST PAYABLE
    # -------------------------
    elif note_id == "14":
        # For WELFARE: Interest is 0 (no interest charged on welfare loans)
        data.append({
            'date': str(year),
            'desc': "WELFARE: No interest charged on welfare loans",
            'amount': 0,
            'type': 'in'
        })

    # -------------------------
    # NOTE 16: SHARE CAPITAL
    # -------------------------
    elif note_id == "16":
        records = RegistrationFee.objects.filter(
            paid=True,
            paid_at__year=year
        ).select_related('member')

        for r in records:
            data.append({
                'date': r.paid_at.strftime('%Y-%m-%d') if r.paid_at else '',
                'desc': f"Share Capital - {r.member}",
                'amount': float(r.amount),
                'type': 'in'
            })

    # -------------------------
    # NOTE 17: RESERVES (UPDATED - Includes Bereavement & Expenses)
    # -------------------------
    elif note_id == "17":
        from decimal import Decimal
        from django.db.models import Sum
        
        # ===== 1. TOTAL ASSETS =====
        # Cash from transactions (deposits, repayments, shares)
        total_cash = Transaction.objects.filter(
            created_at__year=year,
            transaction_type__in=['deposit', 'repayment', 'shares']
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        # Loans to members
        total_loans = Loan.objects.filter(
            application_date__year=year,
            status__in=['approved', 'disbursed']
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        total_assets = total_cash + total_loans
        
        # ===== 2. TOTAL LIABILITIES =====
        # Members' deposits (Monthly Contributions)
        total_deposits = MonthlyContribution.objects.filter(
            month__year=year
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        # Expenses (Regular Expenses)
        total_expenses = Expense.objects.filter(
            date_spent__year=year
        ).aggregate(total=Sum('amount_spent'))['total'] or Decimal('0.00')
        
        # Bereavement Payments
        total_bereavement = BereavementPayment.objects.filter(
            payment_year=year,
            status='paid'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        # Total liabilities = Deposits + Expenses + Bereavement
        total_liabilities = total_deposits + total_expenses + total_bereavement
        
        # ===== 3. SHARE CAPITAL =====
        total_shares = RegistrationFee.objects.filter(
            paid=True,
            paid_at__year=year
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        # ===== 4. RESERVES =====
        # Reserves = Total Assets - Total Liabilities - Share Capital
        reserves = total_assets - total_liabilities - total_shares
        
        # ===== 5. BUILD RESPONSE =====
        # Show detailed breakdown for reserves
        data.append({
            'date': str(year),
            'desc': f"RESERVES CALCULATION FOR {year}",
            'amount': 0,
            'type': 'in'
        })
        
        data.append({
            'date': str(year),
            'desc': f"Total Assets (Cash + Loans)",
            'amount': float(total_assets),
            'type': 'in'
        })
        
        data.append({
            'date': str(year),
            'desc': f"Less: Total Liabilities (Deposits + Expenses + Bereavement)",
            'amount': float(total_liabilities),
            'type': 'out'
        })
        
        data.append({
            'date': str(year),
            'desc': f"Less: Share Capital",
            'amount': float(total_shares),
            'type': 'out'
        })
        
        data.append({
            'date': str(year),
            'desc': f"═══════════════════════════════",
            'amount': 0,
            'type': 'in'
        })
        
        data.append({
            'date': str(year),
            'desc': f"RETAINED EARNINGS / SURPLUS",
            'amount': float(reserves),
            'type': 'in' if reserves >= 0 else 'out'
        })

    # -------------------------
    # RESPONSE
    # -------------------------
    return JsonResponse({
        "results": data
    })
def balance_sheet_view(request):
    # Get the year from the query parameters, default to current year
    current_year = timezone.now().year
    year = request.GET.get('year', current_year)
    
    try:
        year = int(year)
    except ValueError:
        year = current_year

    # Generate the formal balance sheet data using the service
    report_data = BalanceSheetService.generate_balance_sheet(year)
    
    # Range for the year selector dropdown
    year_range = range(current_year - 5, current_year + 1)

    return render(request, 'balance_sheet.html', {
        'report': report_data,
        'year_range': year_range,
        'selected_year': year
    })
import datetime

from django.shortcuts import render, get_object_or_404
from django.db.models import Sum
from django.utils import timezone
from decimal import Decimal
from datetime import datetime
from django.contrib.auth.decorators import login_required

from Users.models import Profile
from .models import (
    CapitalShare, MonthlyContribution, Loan, LoanRepayment,
    XmasLoan
)

from django.shortcuts import render, get_object_or_404
from django.db.models import Sum
from django.utils import timezone
from decimal import Decimal
from datetime import datetime
from django.contrib.auth.decorators import login_required

from Users.models import Profile
from .models import (
    CapitalShare, MonthlyContribution, Loan, LoanRepayment,
    XmasLoan
)

@login_required
def my_statement(request):
    user = request.user
    member = get_object_or_404(Profile, user=user)

    year = timezone.now().year
    start_month = int(request.GET.get('start_month', 1))
    end_month = int(request.GET.get('end_month', timezone.now().month))

    start_month = max(1, min(12, start_month))
    end_month = max(1, min(12, end_month))
    if start_month > end_month:
        start_month, end_month = end_month, start_month

    # --- OPENING BALANCES (before current year) ---

    # 1. Capital Shares – using `month` field (DateField) for reliability
    initial_shares = CapitalShare.objects.filter(
        member=member,
        month__year__lt=year
    ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')

    # 2. Savings (Welfare)
    opening_savings = MonthlyContribution.objects.filter(
        member=member,
        month__year__lt=year
    ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')

    # 3. Normal Loans – opening balance = principal remaining (using get_remaining_balance which includes interest, but we'll separate interest later)
    opening_loans = Loan.objects.filter(member=member, application_date__year__lt=year)
    opening_loan_bal = sum([l.get_remaining_balance() for l in opening_loans])  # total remaining (principal+interest)

    # 4. Xmas Loans – opening balance = total remaining (principal+interest)
    opening_xmas = XmasLoan.objects.filter(member=member, application_date__year__lt=year)
    opening_xmas_bal = sum([l.remaining_balance for l in opening_xmas])

    # We also need opening interest balance? For simplicity, we track cumulative interest charged from start of year.
    # Opening interest is not tracked separately; we start from 0 and accumulate interest charged during the year.
    # However, the opening loan balances already include interest from prior years, but we don't separate that.
    # We'll just accumulate interest charged this year.

    # Initialize running totals (principal balances)
    running_shares = initial_shares
    running_savings = opening_savings
    running_loan = opening_loan_bal      # total remaining (principal+interest)
    running_xmas = opening_xmas_bal      # total remaining (principal+interest)
    running_interest_bal = Decimal('0')  # cumulative interest charged this year

    monthly_stats = []

    for m in range(start_month, end_month + 1):
        # 1. Capital Shares (using `month` field)
        shares = CapitalShare.objects.filter(
            member=member,
            month__year=year,
            month__month=m
        )
        s_in = shares.filter(amount__gt=0).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        s_out = abs(shares.filter(amount__lt=0).aggregate(Sum('amount'))['amount__sum'] or Decimal('0'))
        running_shares += (s_in - s_out)

        # 2. Monthly Savings (Welfare)
        savings = MonthlyContribution.objects.filter(
            member=member,
            month__year=year,
            month__month=m
        )
        sav_in = savings.aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        running_savings += sav_in

        # 3. Normal Loans
        loans = Loan.objects.filter(
            member=member,
            application_date__year=year,
            application_date__month=m,
            status='disbursed'
        )
        # Principal disbursed (amount)
        l_disbursed = loans.aggregate(Sum('amount'))['amount__sum'] or Decimal('0')

        # Repayments for normal loans (exclude Xmas repayments)
        l_repaid = LoanRepayment.objects.filter(
            member=member,
            payment_date__year=year,
            payment_date__month=m,
            is_xmas=False
        ).aggregate(Sum('amount_paid'))['amount_paid__sum'] or Decimal('0')

        # Interest charged on normal loans (if any, e.g., legacy)
        l_interest = loans.aggregate(Sum('interest'))['interest__sum'] or Decimal('0')

        # Update running loan balance (total remaining = principal + interest)
        # We add total_payable (principal+interest) of new loans and subtract repayments
        # But we only have principal disbursed and interest separately, so we add both.
        running_loan += (l_disbursed + l_interest - l_repaid)

        # 4. Xmas Loans
        xmas_loans = XmasLoan.objects.filter(
            member=member,
            application_date__year=year,
            application_date__month=m,
            status='disbursed'
        )
        # Disbursed amount = total payable (principal + interest)
        x_disbursed = sum([loan.total_payable for loan in xmas_loans])  # Decimal
        # Interest charged on xmas loans (total interest)
        x_interest = sum([loan.total_interest for loan in xmas_loans])

        # Xmas repayments
        x_repaid = LoanRepayment.objects.filter(
            member=member,
            payment_date__year=year,
            payment_date__month=m,
            is_xmas=True
        ).aggregate(Sum('amount_paid'))['amount_paid__sum'] or Decimal('0')

        running_xmas += (x_disbursed - x_repaid)

        # Accumulate total interest charged this year (both normal and xmas)
        running_interest_bal += (l_interest + x_interest)

        monthly_stats.append({
            'date': datetime(year, m, 1),
            'share_received': s_in if s_in else None,
            'share_withdrawn': s_out if s_out else None,
            'running_share_bal': running_shares,
            'savings_in': sav_in if sav_in else None,
            'running_savings_bal': running_savings,
            'loan_disbursed': l_disbursed if l_disbursed else None,
            'loan_repaid': l_repaid if l_repaid else None,
            'running_loan_bal': running_loan,
            'xmas_disbursed': x_disbursed if x_disbursed else None,
            'xmas_repaid': x_repaid if x_repaid else None,
            'running_xmas_bal': running_xmas,
            'interest_paid': None,   # not tracked separately; we only show interest charged
            'interest_bal': running_interest_bal,
        })

    context = {
        'member': member,
        'monthly_stats': monthly_stats,
        'initial_shares': initial_shares,
        'initial_savings': opening_savings,
        'initial_loan_bal': opening_loan_bal,
        'initial_xmas_bal': opening_xmas_bal,
        'current_shares': running_shares,
        'current_savings': running_savings,
        'current_loan': running_loan,
        'current_xmas': running_xmas,
        'current_interest_bal': running_interest_bal,
        'start_month': start_month,
        'end_month': end_month,
        'today': timezone.now(),
        'year': year,
        'months': range(1, 13),
    }
    return render(request, 'statement_template.html', context)
def add_expense_view(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES)
        if form.is_valid():
            # Commit=False allows us to attach the user profile before saving
            expense = form.save(commit=False)
            expense.recorded_by = request.user.profile 
            expense.save()
            
            messages.success(request, f"Expense for {expense.get_expense_type_display()} recorded successfully!")
            return redirect('treasurer_dashboard') # Redirect to your ledger
    else:
        form = ExpenseForm()
    
    return render(request, 'add_expense.html', {'form': form})

from django import template

register = template.Library()

@register.filter
def replace(value, arg):
    """
    Usage: {{ value|replace:"_, " }} 
    Replaces the first part of the argument with the second part.
    """
    if len(arg.split(',')) != 2:
        return value
    
    old, new = arg.split(',')
    return value.replace(old, new)
def sacco_report(request, year=None, month=None):
    # Default to current month if not provided
    today = timezone.now()
    report_year = year or today.year
    report_month = month or today.month
    
    # --- FILTERS ---
    # Monthly Contribution uses 'month' field (DateField)
    # Expense uses 'date_spent' (DateField)
    # Loans use 'application_date' (DateTimeField)
    
    # 1. TOTAL SAVINGS THIS MONTH
    monthly_savings = MonthlyContribution.objects.filter(
        month__year=report_year, month__month=report_month
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    monthly_shares = CapitalShare.objects.filter(
        month__year=report_year, month__month=report_month
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    # 2. LOANS DISBURSED THIS MONTH
    normal_loans = Loan.objects.filter(
        status='disbursed', 
        disbursed_at__year=report_year, 
        disbursed_at__month=report_month
    )
    total_normal_disbursed = normal_loans.aggregate(Sum('amount'))['amount__sum'] or 0
    total_normal_interest = normal_loans.aggregate(Sum('interest'))['interest__sum'] or 0
    
    xmas_loans = XmasLoan.objects.filter(
        is_disbursed=True,
        disbursement_date__year=report_year,
        disbursement_date__month=report_month
    )
    total_xmas_disbursed = xmas_loans.aggregate(Sum('amount_requested'))['amount_requested__sum'] or 0
    total_xmas_interest = total_xmas_disbursed * Decimal('0.091')

    # 3. LOAN REPAYMENTS RECEIVED THIS MONTH
    repayments = LoanRepayment.objects.filter(
        payment_date__year=report_year,
        payment_date__month=report_month
    ).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0

    # 4. EXPENDITURE THIS MONTH
    expenses_list = Expense.objects.filter(
        date_spent__year=report_year,
        date_spent__month=report_month
    )
    total_expenses = expenses_list.aggregate(Sum('amount_spent'))['amount_spent__sum'] or 0
    
    # Per Expenditure Breakdown
    expense_breakdown = expenses_list.values('expense_type').annotate(total=Sum('amount_spent'))

    # 5. FINAL CALCULATION
    total_inflow = monthly_savings + monthly_shares + repayments
    net_cash_flow = total_inflow - (total_normal_disbursed + total_xmas_disbursed + total_expenses)

    context = {
        'report_date': datetime(int(report_year), int(report_month), 1),
        'savings': monthly_savings + monthly_shares,
        'repayments': repayments,
        'loans_out': total_normal_disbursed + total_xmas_disbursed,
        'interest_earned': total_normal_interest + total_xmas_interest,
        'expenses': total_expenses,
        'expense_breakdown': expense_breakdown,
        'net_flow': net_cash_flow,
        'inflow': total_inflow,
    }
    
    return render(request, 'sacco.html', context)


import datetime
from django.shortcuts import render
from django.contrib import messages
# Ensure this import exists!
from home.service import SaccoReportService 

def Bank_Statement(request):
    current_year = timezone.now().year
    year = request.GET.get('year', current_year)
    
    try:
        year = int(year)
    except ValueError:
        year = current_year

    report_data = None
    try:
        # The service call that might be failing
        report_data = SaccoReportService.generate_annual_report(year)
    except Exception as e:
        # Log the error for the Architect to see
        print(f"Report Error: {e}") 
        messages.error(request, f"Could not generate report for {year}. Please ensure data exists.")

    year_range = range(current_year - 5, current_year + 1)
    
    return render(request, 'financial_audit.html', {
        'report': report_data,
        'year_range': year_range,
        'selected_year': year
    })


def bank_financial_report(request):
    # --- 1. NORMAL LOANS ---
    # Summing fields already stored in the Loan model (Principal, Interest, Insurance)
    normal_stats = Loan.objects.filter(is_disbursed=True).aggregate(
        principal=Sum('amount'),
        interest=Sum('interest'),
        insurance=Sum('insurance')
    )
    
    normal_interest = normal_stats['interest'] or Decimal('0.00')
    normal_principal = normal_stats['principal'] or Decimal('0.00')
    normal_insurance = normal_stats['insurance'] or Decimal('0.00')

    # --- 2. XMAS LOANS ---
    # Calculating interest based on your 9.1% fixed rate logic
    xmas_principal = XmasLoan.objects.filter(is_disbursed=True).aggregate(
        total=Sum('amount_requested'))['total'] or Decimal('0.00')
    
    xmas_interest = xmas_principal * Decimal('0.091')

    # --- 3. CONSOLIDATED TOTALS ---
    total_principal = normal_principal + xmas_principal
    
    # We keep them separate for the context, but sum them for the grand total
    total_interest_combined = normal_interest + xmas_interest
    
    grand_total = total_principal + total_interest_combined + normal_insurance

    context = {
        # Individual Interests (Separated)
        'normal_interest': normal_interest,
        'xmas_interest': xmas_interest,
        
        # Totals
        'principal': total_principal,
        'insurance': normal_insurance,
        'grand_total': grand_total,
        'report_date': datetime.datetime.now(),
    }
    return render(request, 'bank.html', context)

def member_loan_details_view(request, profile_id):
    # 1. Get the member
    member = get_object_or_404(Profile, id=profile_id)
    
    # 2. Fetch all Normal Loans
    normal_loans = member.member_loans.all().order_by('-application_date')
    
    # 3. Fetch all Xmas Loans
    xmas_loans = member.xmas_loans.all().order_by('-application_date')
    
    context = {
        'member': member,
        'normal_loans': normal_loans,
        'xmas_loans': xmas_loans,
    }
    return render(request, 'member_loans.html', context)


def to_decimal(value):
    try:
        return Decimal(str(value).strip())
    except:
        return Decimal('0.00')


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from decimal import Decimal
from datetime import datetime
from dateutil.relativedelta import relativedelta

from .models import Profile, Loan, LoanRepaymentSchedule, LoanRepayment, Transaction


def to_decimal(value):
    try:
        return Decimal(str(value))
    except:
        return Decimal('0.00')
from decimal import Decimal
from datetime import datetime
from django.db import transaction
from django.db.models import Sum
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from dateutil.relativedelta import relativedelta
from .models import (
    Profile, Loan, LoanRepaymentSchedule, LoanRepayment,
    XmasLoan, CapitalShare, MonthlyContribution
)

# ===================================================================
# MIGRATION FOR REGULAR (WELFARE) LOANS
# ===================================================================
@login_required
@role_required(allowed_roles=['1'])  # Admin only
def migrate_single_member_loan(request, member_id):
    profile = get_object_or_404(Profile, id=member_id)

    # 1️⃣ Total savings from CapitalShare (this is the global cap for welfare loans)
    total_savings = CapitalShare.objects.filter(member=profile).aggregate(
        Sum('amount')
    )['amount__sum'] or Decimal('0.00')
    global_cap = total_savings  # No multiplier for welfare

    # 2️⃣ Other exposure (all existing loans except the one being migrated)
    other_exposure = Loan.objects.filter(member=profile, status__in=['disbursed']).aggregate(
        Sum('amount')
    )['amount__sum'] or Decimal('0.00')
    

    available_limit = global_cap - other_exposure
    if available_limit < 0:
        available_limit = Decimal('0.00')

    if request.method == "POST":
        principal = Decimal(request.POST.get('principal', '0') or '0')
        interest = Decimal(request.POST.get('interest', '0') or '0')
        insurance = Decimal(request.POST.get('insurance', '0') or '0')
        paid_on_paper = Decimal(request.POST.get('paid_on_paper', '0') or '0')
        purpose = request.POST.get('purpose', 'normal')
        duration = int(request.POST.get('duration_months', 12))
        actual_start_date = request.POST.get('start_date')

        try:
            start_date = datetime.strptime(actual_start_date, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            messages.error(request, "Invalid start date format.")
            return redirect(request.path)

        # ❌ Enforce loan limit
        if principal > available_limit:
            messages.error(
                request,
                f"Principal exceeds available limit of KES {available_limit:,.2f}"
            )
            return redirect(request.path)

        with transaction.atomic():
            # Create the loan as disbursed (legacy data)
            loan = Loan.objects.create(
                member=profile,
                amount=principal,
                interest=interest,
                insurance=insurance,
                duration_months=duration,
                purpose=purpose,
                is_legacy=True,               # Mark as migrated
                status='disbursed',
                is_disbursed=True,
                staff_approved=True,
                treasurer_approved=True,
                admin_approved=True,
                application_date=start_date,
                disbursed_at=start_date
            )

            # 🔄 Generate repayment schedule (same as apply_loan logic)
            total_payable = principal + interest + insurance
            monthly_amount = (total_payable / duration).quantize(Decimal('0.01'))
            schedules = []

            for i in range(duration):
                due_date = start_date + relativedelta(months=i + 1)
                schedule = LoanRepaymentSchedule.objects.create(
                    loan=loan,
                    installment_number=i + 1,
                    due_date=due_date,
                    amount_due=monthly_amount,
                    is_paid=False
                )
                schedules.append(schedule)

            # 💰 Handle pre‑paid amounts (paid_on_paper)
            if paid_on_paper > 0:
                repayment = LoanRepayment.objects.create(
                    loan=loan,
                    member=profile,
                    amount_paid=paid_on_paper,
                    reference=f"MIGRATION-PAY-{loan.id}",
                    payment_date=datetime.now().date()
                )

                remaining = paid_on_paper
                for schedule in schedules:
                    if remaining <= 0:
                        break
                    if remaining >= schedule.amount_due:
                        remaining -= schedule.amount_due
                        schedule.amount_paid = schedule.amount_due
                        schedule.is_paid = True
                    else:
                        schedule.amount_paid = remaining
                        remaining = Decimal('0.00')
                    schedule.save()

            # (Optional) Update member account loan limit if you have one

        messages.success(
            request,
            f"Migration successful for {profile.user.get_full_name()}."
        )
        return redirect('admin_dashboard')

    context = {
        'member': profile,
        'available_limit': available_limit,
        'other_exposure': other_exposure,
        'global_cap': global_cap,
    }
    return render(request, 'migrate_form.html', context)


# ===================================================================
# MIGRATION FOR XMAS (HOLIDAY) LOANS
# ===================================================================
@login_required
@role_required(allowed_roles=['1'])  # Admin only
def migrate_xmas_loan(request, member_id):
    profile = get_object_or_404(Profile, id=member_id)

    # Total shares from MonthlyContribution (cap = 3.5 × shares)
    total_shares = MonthlyContribution.objects.filter(member=profile).aggregate(
        Sum('amount')
    )['amount__sum'] or Decimal('0.00')
    max_limit = total_shares * Decimal('3.5')

    # Existing Xmas exposure – exclude finalized loans
    current_xmas_exposure = XmasLoan.objects.filter(member=profile).exclude(
        status__in=['rejected', 'cleared']
    ).aggregate(Sum('amount_requested'))['amount_requested__sum'] or Decimal('0.00')

    available_limit = max_limit - current_xmas_exposure
    if available_limit < 0:
        available_limit = Decimal('0.00')

    if request.method == "POST":
        principal = Decimal(request.POST.get('amount', '0') or '0')
        interest = Decimal(request.POST.get('interest', '0') or '0')
        paid_on_paper = Decimal(request.POST.get('paid_on_paper', '0') or '0')
        duration = int(request.POST.get('duration', 12))
        actual_start_date = request.POST.get('start_date')

        # Validate duration (12–24 months, as per apply_xmas_loan)
        if duration < 12 or duration > 24:
            messages.error(request, "Repayment period must be between 12 and 24 months.")
            return redirect(request.path)

        try:
            start_date = datetime.strptime(actual_start_date, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            messages.error(request, "Invalid start date format.")
            return redirect(request.path)

        # Enforce loan limit
        if principal > available_limit:
            messages.error(
                request,
                f"Amount exceeds available limit of KES {available_limit:,.2f}"
            )
            return redirect(request.path)

        with transaction.atomic():
            # Create the Xmas loan as disbursed
            xmas_loan = XmasLoan.objects.create(
                member=profile,
                amount_requested=principal,
                is_legacy=True,
                manual_interest_amount=interest,
                repayment_period=duration,
                installments=duration,
                status='disbursed',
                is_disbursed=True,
                staff_approved=True,
                treasurer_approved=True,
                admin_approved=True,
                disbursement_date=datetime.combine(start_date, datetime.min.time()),
                approval_date=datetime.now()
            )

            # Generate repayment schedule for the selected duration
            total_payable = principal + interest
            monthly_amount = (total_payable / duration).quantize(Decimal('0.01'))

            schedules = []
            for i in range(duration):
                due_date = start_date + relativedelta(months=i + 1)
                schedule = LoanRepaymentSchedule.objects.create(
                    xmas_loan=xmas_loan,
                    installment_number=i + 1,
                    due_date=due_date,
                    amount_due=monthly_amount,   # Only amount_due, no principal/interest split
                    is_paid=False,
                    is_xmas=True
                )
                schedules.append(schedule)

            # Handle pre‑paid amounts
            if paid_on_paper > 0:
                LoanRepayment.objects.create(
                    xmas_loan=xmas_loan,
                    member=profile,
                    amount_paid=paid_on_paper,
                    reference=f"XMAS-MIG-{xmas_loan.id}",
                    is_xmas=True,
                    payment_date=datetime.now().date()
                )

                remaining = paid_on_paper
                for schedule in schedules:
                    if remaining <= 0:
                        break
                    if remaining >= schedule.amount_due:
                        remaining -= schedule.amount_due
                        schedule.amount_paid = schedule.amount_due
                        schedule.is_paid = True
                    else:
                        schedule.amount_paid = remaining
                        remaining = Decimal('0.00')
                    schedule.save()

        messages.success(
            request,
            f"Xmas migration successful for {profile.user.get_full_name()}."
        )
        return redirect('admin_dashboard')

    # Pass duration choices (12–24) to the template
    context = {
        'member': profile,
        'max_limit': max_limit,
        'current_exposure': current_xmas_exposure,
        'available_limit': available_limit,
        'duration_choices': range(12, 25),  # 12 to 24 inclusive
    }
    return render(request, 'migrate_xmas_form.html', context)
# views.py

@login_required
def bereavement_settings(request):
    profile = request.user.profile
    
    # Get or create bereavement settings for the member
    settings, created = BereavementContribution.objects.get_or_create(
        member=profile,
        defaults={
            'spouse_amount': 0.00,
            'child_amount': 0.00,
            'parent_amount': 0.00,
        }
    )
    
    if request.method == 'POST':
        # Check if admin has announced an amount
        if settings.use_admin_amount and settings.admin_announced_amount:
            messages.warning(request, f"Admin has set a fixed bereavement amount of KES {settings.admin_announced_amount:,.2f}. You cannot change individual amounts.")
            return redirect('bereavement_settings')
        
        spouse = Decimal(request.POST.get('spouse_amount', 0))
        child = Decimal(request.POST.get('child_amount', 0))
        parent = Decimal(request.POST.get('parent_amount', 0))
        
        # Validate range (0 - 100,000)
        if spouse < 0 or spouse > 100000 or child < 0 or child > 100000 or parent < 0 or parent > 100000:
            messages.error(request, "Each contribution must be between KES 0 and KES 100,000.")
            return redirect('bereavement_settings')
        
        settings.spouse_amount = spouse
        settings.child_amount = child
        settings.parent_amount = parent
        settings.save()
        
        messages.success(request, "Your bereavement contribution settings have been updated successfully!")
        return redirect('member_dashboard')
    
    context = {
        'settings': settings,
        'total': settings.total_monthly,
        'is_admin_announced': settings.is_admin_announced and settings.use_admin_amount,
    }
    return render(request, 'bereavement_settings.html', context)


@login_required
def bereavement_admin(request):
    # Admin view to see all member bereavement settings
    if request.user.user_type not in ['1', '2', '3'] and not request.user.is_superuser:
        messages.error(request, "Unauthorized access.")
        return redirect('member_dashboard')
    
    settings = BereavementContribution.objects.select_related('member').all().order_by('-created_at')
    
    # Handle admin announcement
    if request.method == 'POST':
        if request.user.user_type not in ['1', '3'] and not request.user.is_superuser:
            messages.error(request, "Only Admin or Treasurer can announce bereavement amounts.")
            return redirect('bereavement_admin')
        
        member_id = request.POST.get('member_id')
        announced_amount = request.POST.get('announced_amount')
        use_admin_amount = request.POST.get('use_admin_amount') == 'on'
        
        try:
            member = Profile.objects.get(id=member_id)
            setting = BereavementContribution.objects.get(member=member)
        except (Profile.DoesNotExist, BereavementContribution.DoesNotExist):
            messages.error(request, "Member or settings not found.")
            return redirect('bereavement_admin')
        
        if announced_amount:
            amount = Decimal(announced_amount)
            if amount < 0 or amount > 100000:
                messages.error(request, "Amount must be between KES 0 and KES 100,000.")
                return redirect('bereavement_admin')
            
            setting.admin_announced_amount = amount
            setting.admin_announced_date = timezone.now()
            setting.admin_announced_by = request.user.profile
            setting.use_admin_amount = use_admin_amount
            setting.save()
            
            messages.success(request, f"Bereavement amount of KES {amount:,.2f} announced for {member.user.get_full_name()}.")
        else:
            # Clear admin announcement
            setting.admin_announced_amount = None
            setting.admin_announced_date = None
            setting.admin_announced_by = None
            setting.use_admin_amount = False
            setting.save()
            messages.success(request, f"Admin announcement cleared for {member.user.get_full_name()}.")
        
        return redirect('bereavement_admin')
    
    context = {
        'settings': settings,
        'total_contributors': settings.count(),
        'total_monthly_pool': sum(s.total_monthly for s in settings),
    }
    return render(request, 'bereavement_admin.html', context)


@login_required
def bereavement_clear_announcement(request, setting_id):
    # Clear admin announcement for a specific member
    if request.user.user_type not in ['1', '3'] and not request.user.is_superuser:
        messages.error(request, "Unauthorized access.")
        return redirect('bereavement_admin')
    
    try:
        setting = BereavementContribution.objects.get(id=setting_id)
        setting.admin_announced_amount = None
        setting.admin_announced_date = None
        setting.admin_announced_by = None
        setting.use_admin_amount = False
        setting.save()
        messages.success(request, f"Admin announcement cleared for {setting.member.user.get_full_name()}.")
    except BereavementContribution.DoesNotExist:
        messages.error(request, "Setting not found.")
    
    return redirect('bereavement_admin')

@login_required
def treasurer_bereavement_pay(request):
    if request.user.user_type != '3':
        messages.error(request, "Unauthorized access.")
        return redirect('treasurer_dashboard')

    today = timezone.now().date()
    current_month = today.month
    current_year = today.year

    members = Profile.objects.filter(user__is_active=True).order_by('user__first_name', 'user__last_name')

    search_query = request.GET.get('search', '')
    if search_query:
        members = members.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(membership_number__icontains=search_query)
        )

    member_data = []
    for member in members:
        active_anns = BereavementAnnouncement.objects.filter(
            is_active=True,
            is_approved=True
        ).exclude(member=member)

        monthly_due = Decimal('0.00')
        total_instalments = 0
        paid_instalments = 0
        next_due_month = None
        next_due_year = None
        next_due_announcement = None

        for ann in active_anns:
            # Check if active this month
            end_month = ann.start_month + ann.repayment_months - 1
            end_year = ann.start_year
            while end_month > 12:
                end_month -= 12
                end_year += 1

            if (ann.start_year < current_year) or (ann.start_year == current_year and ann.start_month <= current_month):
                if (end_year > current_year) or (end_year == current_year and end_month >= current_month):
                    # Active this month
                    total_instalments += 1
                    # Check paid instalments for this announcement
                    paid = BereavementPayment.objects.filter(
                        member=member,
                        announcement=ann,
                        status='paid'
                    ).count()
                    paid_instalments += paid

                    # Check if already paid for current month
                    payment_exists = BereavementPayment.objects.filter(
                        member=member,
                        announcement=ann,
                        payment_month=current_month,
                        payment_year=current_year,
                        status='paid'
                    ).exists()
                    if not payment_exists:
                        monthly_due += ann.monthly_amount_per_member
                        # Determine next due date (current month if not paid, else next month)
                        if not payment_exists:
                            next_due_month = current_month
                            next_due_year = current_year
                            next_due_announcement = ann
                        else:
                            # Find next month after current month within period
                            next_m = current_month + 1
                            next_y = current_year
                            if next_m > 12:
                                next_m = 1
                                next_y += 1
                            # Check if next month is still within period
                            if (end_year > next_y) or (end_year == next_y and end_month >= next_m):
                                if next_due_month is None or (next_y < next_due_year or (next_y == next_due_year and next_m < next_due_month)):
                                    next_due_month = next_m
                                    next_due_year = next_y
                                    next_due_announcement = ann

        # If no pending due, find the next due date after current month
        if monthly_due == 0:
            # Check if there are any upcoming months
            for ann in active_anns:
                end_month = ann.start_month + ann.repayment_months - 1
                end_year = ann.start_year
                while end_month > 12:
                    end_month -= 12
                    end_year += 1
                # Check if there is any unpaid month in the future
                # We'll just check if there are any payments missing after current month
                # Simple: check if paid_instalments < total_instalments for this ann
                # But we need to find the next unpaid month
                # For simplicity, we'll compute the next month after current month
                next_m = current_month + 1
                next_y = current_year
                if next_m > 12:
                    next_m = 1
                    next_y += 1
                # Check if this future month is within period
                if (ann.start_year < next_y) or (ann.start_year == next_y and ann.start_month <= next_m):
                    if (end_year > next_y) or (end_year == next_y and end_month >= next_m):
                        # Check if payment exists for that future month
                        paid_future = BereavementPayment.objects.filter(
                            member=member,
                            announcement=ann,
                            payment_month=next_m,
                            payment_year=next_y,
                            status='paid'
                        ).exists()
                        if not paid_future:
                            if next_due_month is None or (next_y < next_due_year or (next_y == next_due_year and next_m < next_due_month)):
                                next_due_month = next_m
                                next_due_year = next_y
                                next_due_announcement = ann

        is_paid = monthly_due == 0

        # Determine next due label
        next_due_label = ""
        if next_due_month and next_due_year and next_due_announcement:
            next_due_label = f"{next_due_month:02d}/{next_due_year} - {next_due_announcement.deceased_name}"
        elif is_paid:
            next_due_label = "All paid"

        member_data.append({
            'member': member,
            'monthly_due': monthly_due,
            'is_paid': is_paid,
            'has_paid_this_month': monthly_due == 0,
            'paid_instalments': paid_instalments,
            'total_instalments': total_instalments,
            'next_due_label': next_due_label,
            'next_due_month': next_due_month,
            'next_due_year': next_due_year,
            'next_due_announcement': next_due_announcement,
        })

    # --- POST ---
    if request.method == 'POST':
        member_ids = request.POST.getlist('member_ids')
        if not member_ids:
            messages.error(request, "No members selected.")
            return redirect('treasurer_bereavement_pay')

        success_count = 0
        error_count = 0
        skipped_count = 0

        for member_id in member_ids:
            try:
                member = Profile.objects.get(id=member_id)
                active_anns = BereavementAnnouncement.objects.filter(
                    is_active=True,
                    is_approved=True
                ).exclude(member=member)

                anns_to_pay = []
                for ann in active_anns:
                    end_month = ann.start_month + ann.repayment_months - 1
                    end_year = ann.start_year
                    while end_month > 12:
                        end_month -= 12
                        end_year += 1
                    if (ann.start_year < current_year) or (ann.start_year == current_year and ann.start_month <= current_month):
                        if (end_year > current_year) or (end_year == current_year and end_month >= current_month):
                            payment_exists = BereavementPayment.objects.filter(
                                member=member,
                                announcement=ann,
                                payment_month=current_month,
                                payment_year=current_year,
                                status='paid'
                            ).exists()
                            if not payment_exists:
                                anns_to_pay.append(ann)

                if not anns_to_pay:
                    skipped_count += 1
                    continue

                for ann in anns_to_pay:
                    BereavementPayment.objects.create(
                        member=member,
                        announcement=ann,
                        amount=ann.monthly_amount_per_member,
                        payment_month=current_month,
                        payment_year=current_year,
                        status='paid',
                        reference=f"TREASURER-{timezone.now().strftime('%Y%m%d%H%M%S')}-{member.id}-{ann.id}",
                        notes=f"Monthly payment for {ann.deceased_name}"
                    )
                success_count += 1

            except Profile.DoesNotExist:
                error_count += 1
                continue
            except Exception as e:
                error_count += 1
                continue

        if success_count > 0:
            messages.success(request, f"Successfully recorded payments for {success_count} member(s).")
        if skipped_count > 0:
            messages.warning(request, f"Skipped {skipped_count} member(s) with no pending payment.")
        if error_count > 0:
            messages.error(request, f"Failed to process {error_count} member(s).")

        return redirect('treasurer_bereavement_pay')

    # --- totals ---
    total_collected = BereavementPayment.objects.filter(
        payment_month=current_month,
        payment_year=current_year,
        status='paid'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    context = {
        'member_data': member_data,
        'search_query': search_query,
        'month': today.strftime('%B %Y'),
        'total_members': len(member_data),
        'paid_count': sum(1 for m in member_data if m['is_paid']),
        'pending_count': sum(1 for m in member_data if not m['is_paid']),
        'total_collected': total_collected,
    }
    return render(request, 'treasurer_bereavement_pay.html', context)
# views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from decimal import Decimal
from .models import Profile, BereavementAnnouncement, BereavementPayment


@login_required
def bereavement_admin_create(request):
    """Admin view to create bereavement announcements with start month/year control"""
    # Authorisation
    if request.user.user_type not in ['1', '2', '3'] and not request.user.is_superuser:
        messages.error(request, "Unauthorized access.")
        return redirect('member_dashboard')

    # Common data for GET and POST
    members = Profile.objects.all().order_by('user__first_name', 'user__last_name')
    announcements = BereavementAnnouncement.objects.filter(is_active=True).order_by('-created_at')
    active_members = Profile.objects.filter(user__is_active=True)

    if request.method == 'POST':
        # Get form data
        member_id = request.POST.get('member_id')
        deceased_name = request.POST.get('deceased_name')
        relationship = request.POST.get('relationship')
        total_amount = request.POST.get('total_treasury_amount')
        repayment_months = request.POST.get('repayment_months')
        start_month = request.POST.get('start_month')
        start_year = request.POST.get('start_year')

        # Validate required fields
        if not all([member_id, deceased_name, relationship, total_amount, repayment_months, start_month, start_year]):
            messages.error(request, "All fields are required.")
            return redirect('bereavement_admin_create')

        try:
            member = Profile.objects.get(id=member_id)
            total_amount = Decimal(total_amount)
            repayment_months = int(repayment_months)
            start_month = int(start_month)
            start_year = int(start_year)

            # ============================================================
            # NEW: Enforce exact welfare contribution amount (KES 100,000)
            # ============================================================
            FIXED_AMOUNT = Decimal('100000.00')
            if total_amount != FIXED_AMOUNT:
                messages.error(request, f"Total amount must be exactly KES {FIXED_AMOUNT:,.2f}.")
                return redirect('bereavement_admin_create')

            if total_amount <= 0 or repayment_months <= 0:
                messages.error(request, "Amount and months must be positive.")
                return redirect('bereavement_admin_create')
            if not (1 <= start_month <= 12) or start_year < 2000:
                messages.error(request, "Invalid start month or year.")
                return redirect('bereavement_admin_create')

            # Active members count
            active_count = active_members.count()
            if active_count == 0:
                messages.error(request, "No active members found.")
                return redirect('bereavement_admin_create')

            # Calculate monthly amount per member
            monthly_amount = round(total_amount / active_count / repayment_months, 2)

            # Create announcement with start month/year
            announcement = BereavementAnnouncement.objects.create(
                member=member,
                deceased_name=deceased_name.strip(),
                relationship=relationship,
                total_treasury_amount=total_amount,
                repayment_months=repayment_months,
                monthly_amount_per_member=monthly_amount,
                active_members_count=active_count,
                start_month=start_month,
                start_year=start_year,
                announced_by=request.user.profile,
                is_approved=True,
                approved_by=request.user.profile
            )

            # Generate payment records for each month and each active member
            for i in range(repayment_months):
                month = start_month + i
                year = start_year
                while month > 12:
                    month -= 12
                    year += 1

                for member_profile in active_members:
                    BereavementPayment.objects.create(
                        member=member_profile,
                        announcement=announcement,
                        amount=monthly_amount,
                        payment_month=month,
                        payment_year=year,
                        status='pending',
                        reference=f"BEREAV-{announcement.id}-{month}-{year}",
                        notes=f"Payment for {announcement.deceased_name} ({announcement.get_relationship_display()})"
                    )

            # Success message with period details
            end_month = start_month + repayment_months - 1
            end_year = start_year
            while end_month > 12:
                end_month -= 12
                end_year += 1

            messages.success(
                request,
                f"✅ Bereavement created. Each member pays KES {monthly_amount} monthly from {start_month}/{start_year} "
                f"to {end_month}/{end_year} ({repayment_months} months)."
            )
            return redirect('bereavement_admin_create')

        except Profile.DoesNotExist:
            messages.error(request, "Member not found.")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")

        return redirect('bereavement_admin_create')

    # GET request – show form
    context = {
        'members': members,
        'announcements': announcements,
        'active_members_count': active_members.count(),
        'current_month': timezone.now().month,
        'current_year': timezone.now().year,
        'month_choices': range(1, 13),
    }
    return render(request, 'bereavement_admin_create.html', context)

@login_required
def bereavement_admin_delete(request, announcement_id):
    """Delete/clear a bereavement announcement"""
    if request.user.user_type not in ['1', '2', '3'] and not request.user.is_superuser:
        messages.error(request, "Unauthorized access.")
        return redirect('member_dashboard')
    
    try:
        announcement = BereavementAnnouncement.objects.get(id=announcement_id)
        announcement.is_active = False
        announcement.save()
        messages.success(request, "Announcement cleared successfully.")
    except BereavementAnnouncement.DoesNotExist:
        messages.error(request, "Announcement not found.")
    
    return redirect('bereavement_admin_create')
import csv
import io
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import BereavementAnnouncement, Profile

import csv
import io
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import BereavementAnnouncement, Profile

@login_required

def bereavement_collection_report(request):
    # --- Get all members who have at least one announcement (mourners) ---
    mourners = Profile.objects.filter(
        id__in=BereavementAnnouncement.objects.values_list('member_id', flat=True)
    ).order_by('user__first_name', 'user__last_name')

    # --- Filter by mourner ---
    mourner_id = request.GET.get('mourner_id')
    selected_mourner = None
    if mourner_id:
        selected_mourner = get_object_or_404(Profile, id=mourner_id)

    # --- Get announcements (only active and approved) ---
    announcements = BereavementAnnouncement.objects.filter(
        is_active=True,
        is_approved=True
    ).order_by('-created_at')
    if selected_mourner:
        announcements = announcements.filter(member=selected_mourner)

    report_data = []
    total_collected_overall = Decimal('0.00')
    total_expected_overall = Decimal('0.00')

    for ann in announcements:
        total_expected = ann.total_treasury_amount

        # Total collected from all paid payments for this announcement
        total_collected = BereavementPayment.objects.filter(
            announcement=ann,
            status='paid'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        # Number of paid instalments (distinct month/year combinations)
        paid_instalments = BereavementPayment.objects.filter(
            announcement=ann,
            status='paid'
        ).values('payment_month', 'payment_year').distinct().count()

        total_instalments = ann.repayment_months

        # --- Monthly breakdown ---
        monthly_breakdown = []
        for i in range(ann.repayment_months):
            month = ann.start_month + i
            year = ann.start_year
            while month > 12:
                month -= 12
                year += 1
            collected_month = BereavementPayment.objects.filter(
                announcement=ann,
                payment_month=month,
                payment_year=year,
                status='paid'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            monthly_breakdown.append({
                'label': f"{month:02d}/{year}",
                'collected': collected_month,
            })

        # --- Unpaid members (those who have never paid for this announcement) ---
        all_members = Profile.objects.filter(user__is_active=True).exclude(id=ann.member.id)
        paid_members = Profile.objects.filter(
            id__in=BereavementPayment.objects.filter(
                announcement=ann,
                status='paid'
            ).values_list('member_id', flat=True)
        )
        unpaid_members = all_members.exclude(id__in=paid_members.values_list('id', flat=True))

        report_data.append({
            'announcement': ann,
            'mourner': ann.member,
            'deceased_name': ann.deceased_name,
            'relationship': ann.get_relationship_display(),
            'total_expected': total_expected,
            'total_collected': total_collected,
            'collection_rate': (total_collected / total_expected * 100) if total_expected > 0 else 0,
            'paid_instalments': paid_instalments,
            'total_instalments': total_instalments,
            'unpaid_count': unpaid_members.count(),
            'unpaid_members': unpaid_members[:10],
            'monthly_breakdown': monthly_breakdown,
            'is_active': ann.is_active,
        })

        total_collected_overall += total_collected
        total_expected_overall += total_expected

    # --- CSV Export ---
    if 'export' in request.GET and selected_mourner:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="bereavement_collection_{selected_mourner.user.username}.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'Announcement ID', 'Deceased', 'Relationship', 'Total Expected (KES)',
            'Total Collected (KES)', 'Collection Rate (%)', 'Paid Instalments',
            'Total Instalments', 'Unpaid Members'
        ])
        for item in report_data:
            writer.writerow([
                item['announcement'].id,
                item['deceased_name'],
                item['relationship'],
                f"{item['total_expected']:.2f}",
                f"{item['total_collected']:.2f}",
                f"{item['collection_rate']:.2f}",
                item['paid_instalments'],
                item['total_instalments'],
                item['unpaid_count']
            ])
        return response

    # --- PDF Export ---
    if 'export_pdf' in request.GET and selected_mourner:
        context = {
            'report_data': report_data,
            'total_collected_overall': total_collected_overall,
            'total_expected_overall': total_expected_overall,
            'announcement_count': len(report_data),
            'selected_mourner': selected_mourner,
            'pdf_mode': True,
            'month': "All Time",  # or you can add a date range if needed
        }
        template = get_template('bereavement_collection_report.html')
        html = template.render(context, request)
        result = io.BytesIO()
        pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), result)
        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="bereavement_collection_{selected_mourner.user.username}.pdf"'
            return response
        return HttpResponse('Error generating PDF', status=500)

    # --- Normal GET ---
    context = {
        'report_data': report_data,
        'total_collected_overall': total_collected_overall,
        'total_expected_overall': total_expected_overall,
        'announcement_count': len(report_data),
        'mourners': mourners,
        'selected_mourner': selected_mourner,
        'pdf_mode': False,
        'month': "All Time",
    }
    return render(request, 'bereavement_collection_report.html', context)
@login_required
@login_required
def retirement_admin_create(request):
    """Admin view to create retirement announcements with monthly recovery"""
    if request.user.user_type not in ['1', '2', '3'] and not request.user.is_superuser:
        messages.error(request, "Unauthorized access.")
        return redirect('treasurer_dashboard')

    members = Profile.objects.all().order_by('user__first_name', 'user__last_name')
    announcements = RetirementAnnouncement.objects.filter(is_active=True).order_by('-created_at')
    active_members = Profile.objects.filter(user__is_active=True)

    if request.method == 'POST':
        member_id = request.POST.get('member_id')
        retirement_date = request.POST.get('retirement_date')
        total_amount = request.POST.get('total_target_amount')
        repayment_months = request.POST.get('repayment_months')
        start_month = request.POST.get('start_month')
        start_year = request.POST.get('start_year')

        if not all([member_id, retirement_date, total_amount, repayment_months, start_month, start_year]):
            messages.error(request, "All fields are required.")
            return redirect('retirement_admin_create')

        try:
            member = Profile.objects.get(id=member_id)
            total_amount = Decimal(total_amount)
            repayment_months = int(repayment_months)
            start_month = int(start_month)
            start_year = int(start_year)
            retirement_date = datetime.strptime(retirement_date, '%Y-%m-%d').date()

            # ============================================================
            # NEW: Enforce exact welfare contribution amount (KES 100,000)
            # ============================================================
            FIXED_AMOUNT = Decimal('100000.00')
            if total_amount != FIXED_AMOUNT:
                messages.error(request, f"Total amount must be exactly KES {FIXED_AMOUNT:,.2f}.")
                return redirect('retirement_admin_create')

            if total_amount <= 0 or repayment_months <= 0:
                messages.error(request, "Amount and months must be positive.")
                return redirect('retirement_admin_create')
            if not (1 <= start_month <= 12) or start_year < 2000:
                messages.error(request, "Invalid start month or year.")
                return redirect('retirement_admin_create')

            active_count = active_members.count()
            if active_count == 0:
                messages.error(request, "No active members found.")
                return redirect('retirement_admin_create')

            monthly_amount = round(total_amount / active_count / repayment_months, 2)

            announcement = RetirementAnnouncement.objects.create(
                member=member,
                retirement_date=retirement_date,
                total_target_amount=total_amount,
                repayment_months=repayment_months,
                monthly_amount_per_member=monthly_amount,
                active_members_count=active_count,
                start_month=start_month,
                start_year=start_year,
                announced_by=request.user.profile,
                is_approved=True,
                approved_by=request.user.profile
            )

            # Generate payment records for each member for each month
            for i in range(repayment_months):
                month = start_month + i
                year = start_year
                while month > 12:
                    month -= 12
                    year += 1

                for member_profile in active_members:
                    if member_profile == member:
                        continue  # retiree does not pay for their own retirement
                    RetirementPayment.objects.create(
                        member=member_profile,
                        announcement=announcement,
                        amount=monthly_amount,
                        payment_month=month,
                        payment_year=year,
                        status='pending',
                        reference=f"RETIRE-{announcement.id}-{month}-{year}",
                        notes=f"Retirement payment for {member.user.get_full_name()}"
                    )

            end_month = start_month + repayment_months - 1
            end_year = start_year
            while end_month > 12:
                end_month -= 12
                end_year += 1

            messages.success(
                request,
                f"✅ Retirement announcement created. Each member pays KES {monthly_amount} monthly from {start_month}/{start_year} "
                f"to {end_month}/{end_year} ({repayment_months} months)."
            )
            return redirect('retirement_admin_create')

        except Profile.DoesNotExist:
            messages.error(request, "Member not found.")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")

        return redirect('retirement_admin_create')

    context = {
        'members': members,
        'announcements': announcements,
        'active_members_count': active_members.count(),
        'current_month': timezone.now().month,
        'current_year': timezone.now().year,
        'month_choices': range(1, 13),
    }
    return render(request, 'retirement_admin_create.html', context)
@login_required
def pay_retirement_mpesa(request, announcement_id=None):
    profile = request.user.profile
    today = timezone.now().date()
    current_month = today.month
    current_year = today.year

    # Get all active retirement announcements for this member (excluding own)
    active_announcements = RetirementAnnouncement.objects.filter(
        is_active=True,
        is_approved=True
    ).exclude(member=profile)

    # Filter to only those with pending payment for this month
    pending_announcements = []
    total_due = Decimal('0.00')

    for ann in active_announcements:
        # Check if current month is within repayment period
        end_month = ann.start_month + ann.repayment_months - 1
        end_year = ann.start_year
        while end_month > 12:
            end_month -= 12
            end_year += 1

        in_period = (
            (ann.start_year < current_year) or
            (ann.start_year == current_year and ann.start_month <= current_month)
        ) and (
            (end_year > current_year) or
            (end_year == current_year and end_month >= current_month)
        )

        if in_period:
            # Check if already paid this month
            paid = RetirementPayment.objects.filter(
                member=profile,
                announcement=ann,
                payment_month=current_month,
                payment_year=current_year,
                status='paid'
            ).exists()
            if not paid:
                pending_announcements.append(ann)
                total_due += ann.monthly_amount_per_member

    if total_due == 0:
        messages.info(request, "You have no pending retirement contributions this month.")
        return redirect('member_dashboard')

    if request.method == 'POST':
        phone = request.POST.get('phone')
        if not phone or len(phone) < 10:
            messages.error(request, "Please enter a valid phone number.")
            context = {
                'total_due': total_due,
                'announcements': pending_announcements,
                'month': today.strftime('%B %Y'),
                'phone_number': profile.phone_number or '',
            }
            return render(request, 'pay_retirement_mpesa.html', context)

        # Create payment record(s) – we can create one record per announcement or one total record
        # For simplicity, create a single payment for the total due
        payment = RetirementPayment.objects.create(
            member=profile,
            amount=total_due,
            payment_month=current_month,
            payment_year=current_year,
            status='pending',
            reference=f"RETIRE-{timezone.now().strftime('%Y%m%d%H%M%S')}",
            notes=f"Payment covering {len(pending_announcements)} retirement announcements"
        )

        # Initiate STK Push (reuse your initiate_stk_push function)
        request.POST = request.POST.copy()
        request.POST['payment_id'] = payment.id
        request.POST['payment_type'] = 'retirement'
        request.POST['amount'] = str(total_due)
        request.POST['phone'] = phone

        return initiate_stk_push(request)

    context = {
        'total_due': total_due,
        'announcements': pending_announcements,
        'month': today.strftime('%B %Y'),
        'phone_number': profile.phone_number or '',
    }
    return render(request, 'pay_retirement_mpesa.html', context)
@login_required
def retirement_admin_delete(request, announcement_id):
    """Delete/clear a retirement announcement"""
    if request.user.user_type not in ['1', '2', '3'] and not request.user.is_superuser:
        messages.error(request, "Unauthorized access.")
        return redirect('member_dashboard')
    
    try:
        announcement = RetirementAnnouncement.objects.get(id=announcement_id)
        announcement.is_active = False
        announcement.save()
        messages.success(request, "Announcement cleared successfully.")
    except RetirementAnnouncement.DoesNotExist:
        messages.error(request, "Announcement not found.")
    
    return redirect('retirement_admin_create')
@login_required
@login_required
def treasurer_retirement_pay(request):
    if request.user.user_type != '3':
        messages.error(request, "Unauthorized access.")
        return redirect('treasurer_dashboard')

    today = timezone.now().date()
    
    # Filter month/year from GET or use current
    filter_month = request.GET.get('month')
    filter_year = request.GET.get('year')
    if filter_month:
        try:
            filter_month = int(filter_month)
        except ValueError:
            filter_month = today.month
    else:
        filter_month = today.month
    
    if filter_year:
        try:
            filter_year = int(filter_year)
        except ValueError:
            filter_year = today.year
    else:
        filter_year = today.year

    # Get all active members
    members = Profile.objects.filter(user__is_active=True).order_by('user__first_name', 'user__last_name')

    search_query = request.GET.get('search', '')
    if search_query:
        members = members.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(membership_number__icontains=search_query)
        )

    member_data = []
    for member in members:
        # Get active retirement announcements (exclude own)
        active_anns = RetirementAnnouncement.objects.filter(
            is_active=True,
            is_approved=True
        ).exclude(member=member)

        announcements = []
        total_monthly_due = Decimal('0.00')

        for ann in active_anns:
            # Check if announcement is active in the selected month
            end_month = ann.start_month + ann.repayment_months - 1
            end_year = ann.start_year
            while end_month > 12:
                end_month -= 12
                end_year += 1

            in_period = (
                (ann.start_year < filter_year) or
                (ann.start_year == filter_year and ann.start_month <= filter_month)
            ) and (
                (end_year > filter_year) or
                (end_year == filter_year and end_month >= filter_month)
            )

            if not in_period:
                continue  # skip if not in the selected month's repayment period

            # Check if paid for this month
            paid_this_month = RetirementPayment.objects.filter(
                member=member,
                announcement=ann,
                payment_month=filter_month,
                payment_year=filter_year,
                status='paid'
            ).exists()

            # Count total and paid instalments for this announcement
            total_inst = ann.repayment_months
            paid_inst = RetirementPayment.objects.filter(
                member=member,
                announcement=ann,
                status='paid'
            ).count()

            # Find next due month for this announcement (first unpaid month)
            next_due_month = None
            next_due_year = None
            for i in range(ann.repayment_months):
                m = ann.start_month + i
                y = ann.start_year
                while m > 12:
                    m -= 12
                    y += 1
                paid = RetirementPayment.objects.filter(
                    member=member,
                    announcement=ann,
                    payment_month=m,
                    payment_year=y,
                    status='paid'
                ).exists()
                if not paid:
                    next_due_month = m
                    next_due_year = y
                    break

            # Add to announcement details
            announcements.append({
                'retiree': ann.member,
                'retirement_date': ann.retirement_date,
                'monthly_amount': ann.monthly_amount_per_member,
                'paid_instalments': paid_inst,
                'total_instalments': total_inst,
                'next_due_month': next_due_month,
                'next_due_year': next_due_year,
                'paid_this_month': paid_this_month,
            })

            # Add to total due if not paid this month
            if not paid_this_month:
                total_monthly_due += ann.monthly_amount_per_member

        is_paid = total_monthly_due == 0

        member_data.append({
            'member': member,
            'announcements': announcements,
            'total_monthly_due': total_monthly_due,
            'is_paid': is_paid,
        })

    # --- POST (bulk/single payment) ---
    if request.method == 'POST':
        member_ids = request.POST.getlist('member_ids')
        if not member_ids:
            messages.error(request, "No members selected.")
            return redirect('treasurer_retirement_pay')

        success_count = 0
        error_count = 0

        for member_id in member_ids:
            try:
                member = Profile.objects.get(id=member_id)

                # Recalculate due for the selected month
                active_anns = RetirementAnnouncement.objects.filter(
                    is_active=True,
                    is_approved=True
                ).exclude(member=member)

                anns_to_pay = []
                for ann in active_anns:
                    end_month = ann.start_month + ann.repayment_months - 1
                    end_year = ann.start_year
                    while end_month > 12:
                        end_month -= 12
                        end_year += 1

                    in_period = (
                        (ann.start_year < filter_year) or
                        (ann.start_year == filter_year and ann.start_month <= filter_month)
                    ) and (
                        (end_year > filter_year) or
                        (end_year == filter_year and end_month >= filter_month)
                    )

                    if in_period:
                        payment_exists = RetirementPayment.objects.filter(
                            member=member,
                            announcement=ann,
                            payment_month=filter_month,
                            payment_year=filter_year,
                            status='paid'
                        ).exists()
                        if not payment_exists:
                            anns_to_pay.append(ann)

                if not anns_to_pay:
                    continue  # already paid

                # Create payment records per announcement
                for ann in anns_to_pay:
                    RetirementPayment.objects.create(
                        member=member,
                        announcement=ann,
                        amount=ann.monthly_amount_per_member,
                        payment_month=filter_month,
                        payment_year=filter_year,
                        status='paid',
                        reference=f"RET-TREAS-{timezone.now().strftime('%Y%m%d%H%M%S')}-{member.id}-{ann.id}",
                        notes=f"Monthly retirement payment for {ann.member.user.get_full_name()}"
                    )

                success_count += 1

            except Profile.DoesNotExist:
                error_count += 1
            except Exception as e:
                error_count += 1

        if success_count > 0:
            messages.success(request, f"Successfully recorded retirement payments for {success_count} member(s).")
        if error_count > 0:
            messages.error(request, f"Failed to process {error_count} member(s).")

        return redirect('treasurer_retirement_pay')

    # --- Totals for stats ---
    total_collected = RetirementPayment.objects.filter(
        payment_month=filter_month,
        payment_year=filter_year,
        status='paid'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    month_choices = [(i, date(2000, i, 1).strftime('%b')) for i in range(1, 13)]

    context = {
        'member_data': member_data,
        'search_query': search_query,
        'month': date(filter_year, filter_month, 1).strftime('%B %Y'),
        'filter_month': filter_month,
        'filter_year': filter_year,
        'month_choices': month_choices,
        'years': range(2020, 2035),
        'total_members': len(member_data),
        'paid_count': sum(1 for m in member_data if m['is_paid']),
        'pending_count': sum(1 for m in member_data if not m['is_paid']),
        'total_collected': total_collected,
    }
    return render(request, 'treasurer_retirement_pay.html', context)
@login_required
@role_required(allowed_roles=['1', '2', '3'])  # adjust if you don't have this decorator

def retirement_collection_report(request):
    # --- Get all members who have at least one retirement announcement (retirees) ---
    retirees = Profile.objects.filter(
        id__in=RetirementAnnouncement.objects.values_list('member_id', flat=True)
    ).order_by('user__first_name', 'user__last_name')

    # --- Filter by retiree ---
    retiree_id = request.GET.get('retiree_id')
    selected_retiree = None
    if retiree_id:
        selected_retiree = get_object_or_404(Profile, id=retiree_id)

    # --- Get announcements (only active and approved) ---
    announcements = RetirementAnnouncement.objects.filter(
        is_active=True,
        is_approved=True
    ).order_by('-created_at')
    if selected_retiree:
        announcements = announcements.filter(member=selected_retiree)

    report_data = []
    total_collected_overall = Decimal('0.00')
    total_expected_overall = Decimal('0.00')

    for ann in announcements:
        total_expected = ann.total_target_amount

        # Total collected from all paid payments for this announcement
        total_collected = RetirementPayment.objects.filter(
            announcement=ann,
            status='paid'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        # Number of paid instalments (distinct month/year combinations)
        paid_instalments = RetirementPayment.objects.filter(
            announcement=ann,
            status='paid'
        ).values('payment_month', 'payment_year').distinct().count()

        total_instalments = ann.repayment_months

        # --- Monthly breakdown ---
        monthly_breakdown = []
        for i in range(ann.repayment_months):
            month = ann.start_month + i
            year = ann.start_year
            while month > 12:
                month -= 12
                year += 1
            collected_month = RetirementPayment.objects.filter(
                announcement=ann,
                payment_month=month,
                payment_year=year,
                status='paid'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            monthly_breakdown.append({
                'label': f"{month:02d}/{year}",
                'collected': collected_month,
            })

        # --- Unpaid members (those who have never paid for this announcement) ---
        all_members = Profile.objects.filter(user__is_active=True).exclude(id=ann.member.id)
        paid_members = Profile.objects.filter(
            id__in=RetirementPayment.objects.filter(
                announcement=ann,
                status='paid'
            ).values_list('member_id', flat=True)
        )
        unpaid_members = all_members.exclude(id__in=paid_members.values_list('id', flat=True))

        report_data.append({
            'announcement': ann,
            'retiree': ann.member,
            'retirement_date': ann.retirement_date,
            'total_expected': total_expected,
            'total_collected': total_collected,
            'collection_rate': (total_collected / total_expected * 100) if total_expected > 0 else 0,
            'paid_instalments': paid_instalments,
            'total_instalments': total_instalments,
            'unpaid_count': unpaid_members.count(),
            'unpaid_members': unpaid_members[:10],
            'monthly_breakdown': monthly_breakdown,
            'is_active': ann.is_active,
        })

        total_collected_overall += total_collected
        total_expected_overall += total_expected

    # --- CSV Export ---
    if 'export' in request.GET and selected_retiree:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="retirement_collection_{selected_retiree.user.username}.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'Announcement ID', 'Retiree', 'Retirement Date', 'Total Expected (KES)',
            'Total Collected (KES)', 'Collection Rate (%)', 'Paid Instalments',
            'Total Instalments', 'Unpaid Members'
        ])
        for item in report_data:
            writer.writerow([
                item['announcement'].id,
                item['retiree'].user.get_full_name(),
                item['retirement_date'].strftime('%Y-%m-%d'),
                f"{item['total_expected']:.2f}",
                f"{item['total_collected']:.2f}",
                f"{item['collection_rate']:.2f}",
                item['paid_instalments'],
                item['total_instalments'],
                item['unpaid_count']
            ])
        return response

    # --- PDF Export ---
    if 'export_pdf' in request.GET and selected_retiree:
        context = {
            'report_data': report_data,
            'total_collected_overall': total_collected_overall,
            'total_expected_overall': total_expected_overall,
            'announcement_count': len(report_data),
            'selected_retiree': selected_retiree,
            'pdf_mode': True,
            'is_retirement': True,
        }
        template = get_template('retirement_collection_report.html')
        html = template.render(context, request)
        result = io.BytesIO()
        pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), result)
        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="retirement_collection_{selected_retiree.user.username}.pdf"'
            return response
        return HttpResponse('Error generating PDF', status=500)

    # --- Normal GET ---
    context = {
        'report_data': report_data,
        'total_collected_overall': total_collected_overall,
        'total_expected_overall': total_expected_overall,
        'announcement_count': len(report_data),
        'retirees': retirees,
        'selected_retiree': selected_retiree,
        'pdf_mode': False,
        'is_retirement': True,
    }
    return render(request, 'retirement_collection_report.html', context)
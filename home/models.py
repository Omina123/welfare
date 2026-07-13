from django.db import models
from Users.models import Profile

from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
import datetime
from django.core.validators import MinValueValidator,MaxValueValidator
from decimal import Decimal
from django.utils import timezone
from django.db.models import Sum

def generate_transaction_ref(prefix="TX"):
    """Generates a unique reference: TX-20260313-ABC123"""
    date_str = datetime.datetime.now().strftime('%Y%m%d')
    unique_id = str(uuid.uuid4()).upper()[:6]
    return f"{prefix}-{date_str}-{unique_id}"
# -------------------------
# SHARE SETTINGS
# -------------------------
class ShareSettings(models.Model):

    minimum_shares = models.DecimalField(max_digits=10, decimal_places=2)
    share_value = models.DecimalField(max_digits=10, decimal_places=2)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Share Value {self.share_value}"


# -------------------------
# CAPITAL SHARES
# -------------------------
class CapitalShare(models.Model):

    member = models.ForeignKey(Profile, on_delete=models.CASCADE)

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    month =models.DateField()
    date_created=models.DateTimeField(blank=True, null=True)

    

    def __str__(self):
        return f"{self.member} - {self.amount}"


class XmasRefund(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('disbursed', 'Disbursed'),
        ('partially_approved', 'Partially Approved'),
        ('cleared', 'Cleared'),
        ('rejected', 'Rejected')]

    member = models.ForeignKey(Profile, on_delete=models.CASCADE)
    amount_requested = models.DecimalField(max_digits=12, decimal_places=2)
    year = models.IntegerField()
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')
    
    # Tracking Approvals
    staff_approved = models.BooleanField(default=False)
    treasurer_approved = models.BooleanField(default=False)
    admin_approved = models.BooleanField(default=False)
    
    date_applied = models.DateTimeField(auto_now_add=True)
    date_disbursed = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.member.user.get_full_name()} - {self.year} ({self.status})"
# -------------------------
# MONTHLY CONTRIBUTIONS
# -------------------------
class MonthlyContribution(models.Model):

    member = models.ForeignKey(Profile, on_delete=models.CASCADE,related_name='saving_records')

    amount = models.IntegerField(null=True, blank=True)

    month = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.member} - {self.month}"
class LoanPurpose(models.Model):
    name=models.CharField(max_length=60, null=True, blank=True)
    
    

class CapitalShareRefund(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('staff_approved', 'Staff Approved'),
        ('treasurer_approved', 'Treasurer Approved'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('disbursed', 'Disbursed'),
    ]

    REASON_CHOICES = [
        ('exit', 'Exit from SACCO'),
        ('emergency', 'Emergency'),
        ('other', 'Other'),
    ]

    member = models.ForeignKey(Profile, on_delete=models.CASCADE)
    amount_requested = models.DecimalField(max_digits=12, decimal_places=2)
    year = models.IntegerField(default=timezone.now().year)

    reason = models.CharField(max_length=50, choices=REASON_CHOICES)

    net_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')

    staff_approved = models.BooleanField(default=False)
    treasurer_approved = models.BooleanField(default=False)
    admin_approved = models.BooleanField(default=False)

    date_applied = models.DateTimeField(auto_now_add=True)
    effective_date = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.member.user.username} - Share Refund {self.amount_requested}"
    ...

    
    @property
    def is_cancellable(self):
        """
        Member can only cancel before any approval is done.
        """
        return (
            self.status == 'pending'
            and not self.staff_approved
            and not self.treasurer_approved
            and not self.admin_approved
        )

    @property
    def time_remaining(self):
        """Returns the seconds remaining until the effective date."""
        if self.effective_date:
            remaining = self.effective_date - timezone.now()
            return max(remaining.total_seconds(), 0)
        return 0
class XmasLoan(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('disbursed', 'Disbursed'),
        ('partially_approved', 'Partially Approved'),
        ('cleared', 'Cleared'),
        ('rejected', 'Rejected'),
    ]

    member = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='xmas_loans')
    amount_requested = models.DecimalField(max_digits=12, decimal_places=2)

    is_legacy = models.BooleanField(default=False, help_text="True if this loan was migrated from paper records.")
    manual_interest_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text="Override interest for paper records.")

    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=20.00)  # Changed to 20%
    repayment_period = models.IntegerField(default=12)  # Changed to 12 months
    installments = models.IntegerField(default=12)  # Changed to 12 months

    application_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Approval Workflow
    staff_approved = models.BooleanField(default=False)
    treasurer_approved = models.BooleanField(default=False)
    admin_approved = models.BooleanField(default=False)

    approval_date = models.DateTimeField(null=True, blank=True)
    disbursement_date = models.DateTimeField(null=True, blank=True)
    is_disbursed = models.BooleanField(default=False)

    @property
    def total_interest(self):
        """Returns manual interest for legacy loans, otherwise calculates 20%."""
        if self.is_legacy and self.manual_interest_amount is not None:
            return self.manual_interest_amount
        return self.amount_requested * Decimal('0.20')  # 20% interest

    @property
    def total_payable(self):
        return (self.amount_requested or Decimal('0')) + self.total_interest

    @property
    def monthly_installment(self):
        if self.installments and self.installments > 0:
            return self.total_payable / Decimal(self.installments)
        return Decimal('0.00')

    @property
    def max_eligible_amount(self):
        from .models import CapitalShare
        total_shares = CapitalShare.objects.filter(member=self.member).aggregate(
            Sum('amount')
        )['amount__sum'] or Decimal('0.00')
        return total_shares * Decimal('0.10')

    @property
    def total_paid(self):
        from .models import LoanRepayment
        return LoanRepayment.objects.filter(
            xmas_loan=self,
            is_xmas=True
        ).aggregate(Sum('amount_paid'))['amount_paid__sum'] or Decimal('0.00')

    @property
    def remaining_balance(self):
        return max(self.total_payable - self.total_paid, Decimal('0.00'))
    
    @property
    def approval_progress(self):
        """Returns the number of approvals (0-3)"""
        return int(self.admin_approved) + int(self.staff_approved) + int(self.treasurer_approved)
    
    @property
    def is_fully_approved(self):
        """Returns True if all 3 approvals are done"""
        return self.admin_approved and self.staff_approved and self.treasurer_approved

    def save(self, *args, **kwargs):
        # ===== FIX: Auto-update status based on approvals =====
        if self.is_fully_approved and self.status == 'pending':
            self.status = 'approved'
            self.approval_date = timezone.now()
        
        # If already approved but not disbursed, keep it approved
        if self.is_fully_approved and self.status == 'approved' and not self.is_disbursed:
            pass  # Keep it as approved
        
        super().save(*args, **kwargs)

    def __str__(self):
        type_prefix = "Legacy " if self.is_legacy else ""
        return f"{type_prefix}Holiday Loan - {self.member.user.username} ({self.status})"
# LOANS
# -------------------------



# class Loan(models.Model):
#     STATUS = (
#         ('pending_hr_update', 'Pending HR Salary Update'),
#         ('failed', 'Failed'),

#         ('pending_guarantors', 'Pending Guarantors'),
#         ('pending', 'Pending Approval'),
#         ('approved', 'Approved'),
#         ('partially_approved', 'Partially Approved'),
#         ('disbursed', 'Disbursed'),
#         ('defaulted', 'Defaulted'),
#         ('completed', 'Completed'),
#         ('rejected', 'Rejected'),
#     )
    
#     PURPOSE_CHOICES = (
#     ('normal', 'Normal Loan'),
#     ('school_fees', 'School Fees'),
#     ('emergency', 'Emergency'),
#     ('personal', 'Personal'),
# )
#     member = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="member_loans")
#     purpose = models.CharField(max_length=50, choices=PURPOSE_CHOICES, default='normal Loan')
    
#     amount = models.DecimalField(max_digits=12, decimal_places=2)
#     interest_rate = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('25.90'))
    
#     # Auto-calculated fields
#     insurance = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, editable=False)
#     interest = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, editable=False)
    
#     is_topup = models.BooleanField(default=False)
#     replaces_loan = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)

#     duration_months = models.IntegerField(
#         validators=[MinValueValidator(1), MaxValueValidator(48)]
#     )
#     rejection_reason = models.TextField(
#         blank=True,
#         null=True
#     )

#     status = models.CharField(max_length=20, choices=STATUS, default='pending')
    
#     # Approval Flow
#     admin_approved = models.BooleanField(default=False)
#     staff_approved = models.BooleanField(default=False)
#     treasurer_approved = models.BooleanField(default=False)

#     application_date = models.DateTimeField(auto_now_add=True)
#     approval_date = models.DateTimeField(null=True, blank=True)
#     is_disbursed = models.BooleanField(default=False)
#     disbursed_at = models.DateTimeField(null=True, blank=True)
#     is_legacy = models.BooleanField(default=False, help_text="True if migrated from paper records")
#     legacy_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text="Balance brought forward from paper")

#     def save(self, *args, **kwargs):
#         if not self.is_legacy:
#             # Your existing Tiered Interest Logic here
#             P = Decimal(str(self.amount))
#             # ... calculation logic ...
#         else:
#             # For Legacy: If interest/insurance isn't set, default to 0 to avoid double billing
#             if self.interest is None: self.interest = Decimal('0.00')
#             if self.insurance is None: self.insurance = Decimal('0.00')
            
#         super().save(*args, **kwargs)

#     @property
#     def total_payable(self):
#         """Principal + Interest + Insurance"""
#         return (self.amount or Decimal('0')) + (self.interest or Decimal('0')) + (self.insurance or Decimal('0'))

#     def get_remaining_balance(self):
#         """
#         Calculates the outstanding balance by subtracting total 
#         payments from the total amount due.
#         """
#         # Import inside the method to prevent circular imports with LoanRepayment
#         from .models import LoanRepayment
        
#         total_paid = LoanRepayment.objects.filter(
#             loan=self
#         ).aggregate(Sum('amount_paid'))['amount_paid__sum'] or Decimal('0.00')
        
#         balance = self.total_payable - total_paid
#         return max(balance, Decimal('0.00'))

#     def save(self, *args, **kwargs):
#         """Apply Tiered Interest and SACCO Formulas before saving"""
#         P = Decimal(str(self.amount))
#         M = int(self.duration_months)

#         # 1. Tiered Interest Rate Logic
#         if M <= 12:
#             self.interest_rate = Decimal('9.10')
#             rate_factor = Decimal('0.091')
#         elif M <= 24:
#             self.interest_rate = Decimal('17.50')
#             rate_factor = Decimal('0.175')
#         elif M <= 36:
#             self.interest_rate = Decimal('25.90')
#             rate_factor = Decimal('0.259')
#         else:
#             self.interest_rate = Decimal('34.90')
#             rate_factor = Decimal('0.349')

#         self.interest = rate_factor * P

#         # 2. Insurance Formula: ((5.03 * months + 3.03) * Principal) / 6000
#         M_dec = Decimal(str(M))
#         numerator = (Decimal('5.03') * M_dec + Decimal('3.03')) * P
#         self.insurance = numerator / Decimal('6000')

#         # 3. Status Transition Logic
#         if self.admin_approved and self.staff_approved and self.treasurer_approved:
#             if self.status not in ['disbursed', 'completed', 'defaulted']:
#                 self.status = 'approved'

#         super().save(*args, **kwargs)
#     @property
#     def monthly_installment(self):
#         if self.duration_months:
#             return self.total_payable / Decimal(self.duration_months)
#         return Decimal('0.00')

#     def __str__(self):
#         return f"Loan {self.id} - {self.member.user.username} ({self.status})"
    
#     @property
#     def approval_count(self):
#         """Calculates approval count based on the 3 boolean flags."""
#         count = 0
#         if self.admin_approved: count += 1
#         if self.staff_approved: count += 1
#         if self.treasurer_approved: count += 1
#         return count
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

class Loan(models.Model):
    STATUS = (
        ('pending_hr_update', 'Pending HR Salary Update'),
        ('failed', 'Failed'),
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('partially_approved', 'Partially Approved'),
        ('disbursed', 'Disbursed'),
        ('defaulted', 'Defaulted'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    )
    
    PURPOSE_CHOICES = (
        ('normal', 'Standard Support'),
        ('school_fees', 'Education Support'),
        ('emergency', 'Emergency Support'),
        ('personal', 'Personal Support'),
    )
    
    member = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="member_loans")
    purpose = models.CharField(max_length=50, choices=PURPOSE_CHOICES, default='normal')
    
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    # ===== WELFARE: Interest is always 0 =====
    interest_rate = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # ===== WELFARE: No insurance =====
    insurance = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, default=Decimal('0.00'), editable=False)
    interest = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, default=Decimal('0.00'), editable=False)
    
    # ===== TOP-UP =====
    is_topup = models.BooleanField(default=False)
    replaces_loan = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    
    # ===== WELFARE: Max 24 months (updated from 48) =====
    duration_months = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(24)]
    )
    
    rejection_reason = models.TextField(
        blank=True,
        null=True
    )
    
    status = models.CharField(max_length=20, choices=STATUS, default='pending')
    
    # ===== WELFARE: Approval Flow (No Guarantors Needed) =====
    admin_approved = models.BooleanField(default=False)
    staff_approved = models.BooleanField(default=False)
    treasurer_approved = models.BooleanField(default=False)
    
    application_date = models.DateTimeField(auto_now_add=True)
    approval_date = models.DateTimeField(null=True, blank=True)
    is_disbursed = models.BooleanField(default=False)
    disbursed_at = models.DateTimeField(null=True, blank=True)
    
    is_legacy = models.BooleanField(default=False, help_text="True if migrated from paper records")
    legacy_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text="Balance brought forward from paper")
    
    def save(self, *args, **kwargs):
        """WELFARE: No interest, no insurance, max 24 months"""
        
        if not self.is_legacy:
            # ===== WELFARE: Set interest and insurance to 0 =====
            self.interest_rate = Decimal('0.00')
            self.interest = Decimal('0.00')
            self.insurance = Decimal('0.00')
            
            # ===== WELFARE: Ensure duration doesn't exceed 24 months =====
            if self.duration_months > 24:
                self.duration_months = 24
            
            # ===== Status Transition Logic =====
            if self.admin_approved and self.staff_approved and self.treasurer_approved:
                if self.status not in ['disbursed', 'completed', 'defaulted']:
                    self.status = 'approved'
        else:
            # For Legacy: Keep existing values, default to 0 if not set
            if self.interest is None: self.interest = Decimal('0.00')
            if self.insurance is None: self.insurance = Decimal('0.00')
            
        super().save(*args, **kwargs)
    
    @property
    def total_payable(self):
        """WELFARE: Total payable is just the principal (no interest, no insurance)"""
        return self.amount or Decimal('0')
    
    def get_remaining_balance(self):
        """
        Calculates the outstanding balance by subtracting total 
        payments from the total amount due.
        """
        from .models import LoanRepayment
        
        total_paid = LoanRepayment.objects.filter(
            loan=self
        ).aggregate(models.Sum('amount_paid'))['amount_paid__sum'] or Decimal('0.00')
        
        balance = self.total_payable - total_paid
        return max(balance, Decimal('0.00'))
    
    @property
    def monthly_installment(self):
        """WELFARE: Principal divided by duration months"""
        if self.duration_months and self.duration_months > 0:
            return self.amount / Decimal(self.duration_months)
        return Decimal('0.00')
    
    @property
    def approval_count(self):
        """Calculates approval count based on the 3 boolean flags."""
        count = 0
        if self.admin_approved: count += 1
        if self.staff_approved: count += 1
        if self.treasurer_approved: count += 1
        return count
    
    def __str__(self):
        return f"Loan {self.id} - {self.member.user.username} ({self.status})"
class Guarantor(models.Model):
    STATUS = (
        ('pending', 'Pending Response'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('partially_approved', 'Partially Approved'),
    )

    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    guarantor = models.ForeignKey(Profile, on_delete=models.CASCADE)
    guaranteed_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS, default='pending')

    def __str__(self):
        return f"{self.guarantor} - {self.status} for Loan {self.loan.id}"

    @staticmethod
    def available_guarantors():
        # Exclude those with active loans
        used_guarantors = Guarantor.objects.filter(
            loan__status__in=['pending', 'approved', 'disbursed'],
            status='accepted'
        ).values_list('guarantor_id', flat=True)
        return Profile.objects.exclude(id__in=used_guarantors)

# -------------------------
# LOAN REPAYMENT SCHEDULE
# -------------------------
class LoanRepaymentSchedule(models.Model):
    is_xmas = models.BooleanField(default=False)
    xmas_loan = models.ForeignKey(
        'XmasLoan', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='schedules'
    )
    loan = models.ForeignKey(
        'Loan', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )
    
    installment_number = models.IntegerField()
    due_date = models.DateField()
    
    # WELFARE: Principal only (no interest)
    amount_due = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="WELFARE: Principal installment amount"
    )
    
    is_paid = models.BooleanField(default=False)
    date_paid = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['due_date']
        verbose_name_plural = "Loan Repayment Schedules"

    @property
    def is_overdue(self):
        from django.utils import timezone
        return not self.is_paid and self.due_date < timezone.now().date()

    def __str__(self):
        prefix = "Xmas " if self.is_xmas else ""
        loan_id = self.xmas_loan.id if self.is_xmas else self.loan.id
        return f"{prefix}Loan {loan_id} Installment {self.installment_number} - KES {self.amount_due}"
class HRNotification(models.Model):
    member = models.ForeignKey(Profile, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
# -------------------------
# LOAN REPAYMENTS
# -------------------------
class LoanRepayment(models.Model):

    loan = models.ForeignKey(Loan, on_delete=models.CASCADE,null=True,blank=True)
    xmas_loan = models.ForeignKey(
        'XmasLoan',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='repayments'
    )

    member = models.ForeignKey(Profile, on_delete=models.CASCADE)

    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)

    payment_date = models.DateTimeField(auto_now_add=True)

    reference = models.CharField(max_length=100, blank=True, null=True)
    is_xmas = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.member} - {self.amount_paid}"


# -------------------------
# TRANSACTIONS
# -------------------------
class Transaction(models.Model):

    TRANSACTION_TYPES = (
        ('deposit', 'Deposit'),
        ('loan', 'Loan Disbursement'),
        ('repayment', 'Loan Repayment'),
        ('shares', 'Share Capital'),
    )

    member = models.ForeignKey(Profile, on_delete=models.CASCADE)

    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    reference = models.CharField(max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.member} - {self.transaction_type}"
class ActivityLog(models.Model):
    
    user = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True)

    action = models.CharField(max_length=255)

    ip_address = models.GenericIPAddressField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.action}"



class NormalShares(models.Model):
    member = models.OneToOneField(
        Profile,
        on_delete=models.CASCADE,
        related_name='capital_share'
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(1)],
        help_text="Total committed capital share amount"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.member} - KES {self.amount}"
class RegistrationFee(models.Model):
        member = models.OneToOneField(Profile, on_delete=models.CASCADE)
        amount = models.DecimalField(max_digits=10, decimal_places=2, default=500)
        paid = models.BooleanField(default=False)
        paid_at = models.DateTimeField(null=True, blank=True)

        def __str__(self):
            return f"{self.member} - Registration Fee"
from django.db import models
from django.core.validators import MinValueValidator

class Expense(models.Model):
    # Fixed typo from 'tpye' to 'EXPENSE_TYPES'
    # Using UpperCase for constants is a Django best practice
    EXPENSE_TYPES = [
        ('bank_charge', 'Bank Charges'),
        ('committee_allowance', 'Committee Allowances'),
        ('airtime', 'Airtime'),
        ('cleaning', 'Cleaning Expenses'),
        ('pr', 'Public Relations'),
        ('audit_fees', 'Audit Fees'),
        ('transport', 'Transport'),
        ('stationery', 'Printing and Stationery'),
        ('refreshment', 'Refreshment'),
        ('repairs', 'Office Repairs'),
        ('other', 'Other Expenses'), # Added 'Other' for flexibility
    ]

    # PAYMENT_METHODS for better accounting
    PAYMENT_METHODS = [
        ('cash', 'Petty Cash'),
        ('bank', 'Bank Transfer/Cheque'),
        ('mobile_money', 'Mobile Money'),
    ]

    expense_type = models.CharField(max_length=50, choices=EXPENSE_TYPES)
    
    # Changed from CharField to DecimalField for financial accuracy
    amount_spent = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)] # Prevents negative expenses
    )
    
    date_spent = models.DateField()
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cash')
    
    # Essential for SACCO accountability
    description = models.TextField(blank=True, help_text="Detailed reason for the expense")
    receipt_image = models.ImageField(upload_to='receipts/%Y/%m/', blank=True, null=True)
    recorded_by = models.ForeignKey(Profile, on_delete=models.PROTECT) # Track who added it
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Expenses"
        ordering = ['-date_spent']

    def __str__(self):
        return f"{self.get_expense_type_display()} - {self.amount_spent} ({self.date_spent})"
# models.py

# models.py

class BereavementContribution(models.Model):
    RELATIONSHIP_CHOICES = [
        ('spouse', 'Spouse'),
        ('child', 'Child'),
        ('parent', 'Parent'),
    ]
    
    member = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='bereavement_setting')
    
    # Contribution amounts for each relationship (0 - 100,000)
    spouse_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    child_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    parent_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Admin announced amount (if admin sets a fixed amount)
    admin_announced_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    admin_announced_date = models.DateTimeField(null=True, blank=True)
    admin_announced_by = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name='bereavement_announced_by')
    use_admin_amount = models.BooleanField(default=False)  # If True, member must pay admin amount
    
    # Total monthly contribution
    total_monthly = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, editable=False)
    
    # Status
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        # If admin amount is set and use_admin_amount is True, total is admin amount
        if self.use_admin_amount and self.admin_announced_amount:
            self.total_monthly = self.admin_announced_amount
        else:
            # Calculate total monthly contribution from individual amounts
            self.total_monthly = self.spouse_amount + self.child_amount + self.parent_amount
        super().save(*args, **kwargs)
    
    @property
    def is_admin_announced(self):
        return self.admin_announced_amount is not None and self.admin_announced_amount > 0
    
    def __str__(self):
        return f"{self.member.user.username} - Bereavement Settings"
    
    class Meta:
        verbose_name_plural = "Bereavement Contributions"
# models.py
# models.py


class BereavementAnnouncement(models.Model):
    RELATIONSHIP_CHOICES = [
        ('spouse', 'Spouse'),
        ('child', 'Child'),
        ('parent', 'Parent'),
    ]

    member = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='bereavement_announcements')
    deceased_name = models.CharField(max_length=200)
    relationship = models.CharField(max_length=20, choices=RELATIONSHIP_CHOICES)

    announced_by = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, related_name='announced_bereavements')
    paid_by = models.ManyToManyField(Profile, related_name='paid_bereavements', blank=True)

    # Treasury recovery fields
    total_treasury_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    repayment_months = models.PositiveIntegerField(default=1)
    monthly_amount_per_member = models.DecimalField(max_digits=12, decimal_places=2, editable=False, default=0.00)
    active_members_count = models.PositiveIntegerField(editable=False, default=0)

    # NEW: start month and year for repayment
    start_month = models.PositiveIntegerField(default=1)   # 1-12
    start_year = models.PositiveIntegerField(default=2026)

    # Status
    is_active = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_bereavements')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Bereavement: {self.deceased_name} ({self.get_relationship_display()})"

    class Meta:
        ordering = ['-created_at']


class BereavementPayment(models.Model):
    member = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='bereavement_payments')
    announcement = models.ForeignKey(
        BereavementAnnouncement,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='payments'
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    payment_month = models.IntegerField()
    payment_year = models.IntegerField()
    payment_date = models.DateTimeField(auto_now_add=True)
    reference = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ], default='pending')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-payment_date']

    def __str__(self):
        return f"{self.member.user.username} - {self.payment_month}/{self.payment_year} - KES {self.amount}"
class RetirementAnnouncement(models.Model):
    member = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='retirement_announcements')
    retirement_date = models.DateField(help_text="Date the member retires")
    total_target_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    repayment_months = models.PositiveIntegerField(default=1)
    monthly_amount_per_member = models.DecimalField(max_digits=12, decimal_places=2, editable=False, default=0.00)
    active_members_count = models.PositiveIntegerField(editable=False, default=0)

    start_month = models.PositiveIntegerField(default=1)
    start_year = models.PositiveIntegerField(default=2026)

    announced_by = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, related_name='announced_retirements')
    is_active = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_retirements')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Retirement: {self.member.user.get_full_name()} - {self.retirement_date}"

    class Meta:
        ordering = ['-created_at']


class RetirementPayment(models.Model):
    member = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='retirement_payments')
    announcement = models.ForeignKey(RetirementAnnouncement, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_month = models.IntegerField()
    payment_year = models.IntegerField()
    payment_date = models.DateTimeField(auto_now_add=True)
    reference = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('paid', 'Paid'), ('failed', 'Failed')],
        default='pending'
    )
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.member.user.username} - {self.payment_month}/{self.payment_year} - KES {self.amount}"

    class Meta:
        ordering = ['-payment_date']
class PendingMpesaTransaction(models.Model):
    checkout_request_id = models.CharField(max_length=100, unique=True)
    account_reference = models.CharField(max_length=50)
    member = models.ForeignKey(Profile, on_delete=models.CASCADE)  # ✅ Use 'Profile' as string
    payment_type = models.CharField(max_length=20)  # shares, savings, xmas, loan
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    loan_id = models.CharField(max_length=10, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    receipt_number = models.CharField(max_length=50, null=True, blank=True)
    processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.checkout_request_id} - {self.member.user.username} - {self.payment_type}"
    
    class Meta:
        ordering = ['-created_at']  # ✅ Fixed typo: ordering (not odering)
